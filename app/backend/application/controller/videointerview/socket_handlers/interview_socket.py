import eventlet
from eventlet import tpool
import threading
import logging
import random
import time
import os
from flask import request
from flask_socketio import emit, join_room

# ✅ FIXED: Added missing imports
from ..config import MAXQUESTIONS
from ..services.transcription_service import get_transcription_service
from ..services.question_service import QuestionService
from ..services.recording_service import RecordingService
from ..models.session_store import session_store

logger = logging.getLogger(__name__)
transcription_service = get_transcription_service()
pending_audio_buffers = {}
sid_to_session = {}  # ✅ CRITICAL: Map socket.sid → session_id for disconnect cleanup

# ✅ FIXED: MOVED TO TOP LEVEL - Now accessible by all handlers
def _background_processing(session_id: str):
    """Background: Finalize Video -> AI Evaluation -> Save Data"""
    logger.info(f"🧵 Background processing START for {session_id}")
    
    try:
        # Local imports to avoid circular dependency issues
        from ..models.session_store import session_store
        from ..services.evaluation_service import EvaluationService
        from ..services.recording_service import RecordingService
        
        session = session_store.get(session_id)
        if not session:
            logger.error(f"❌ Session {session_id} expired or not found")
            return

        rec_service = RecordingService()
        eval_service = EvaluationService()

        # 1. HEAVY TASK: Finalize Video/Audio Files
        logger.info("🔧 Finalizing recordings in background...")
        
        if session.video_file and os.path.exists(session.video_file):
            logger.info(f"📹 Finalizing video: {session.video_file}")
            rec_service.finalize_recording(session.video_file)
        
        if session.audio_file and os.path.exists(session.audio_file):
            logger.info(f"🎤 Finalizing audio: {session.audio_file}")
            rec_service.finalize_recording(session.audio_file)

        # 2. HEAVY TASK: AI Evaluation
        logger.info(f"🧠 Starting AI Evaluation for {session_id}")
        evaluation = eval_service.generate_evaluation(session)
        
        # 3. Save Results
        rec_service.save_evaluation(session, evaluation)
        rec_service.save_metadata(session, evaluation)
        rec_service.save_transcript(session)
        
        logger.info(f"✅ Background processing COMPLETE for {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Background processing failed for {session_id}: {e}", exc_info=True)

def init_socketio(socketio):
    logger.info("=" * 70)
    logger.info("🔧 INITIALIZING VIDEO INTERVIEW SOCKET HANDLERS")
    logger.info("=" * 70)

    @socketio.on('joinInterview')
    def handle_join_interview(data):
        """Handle client joining interview - FIXED with ZOMBIE PREVENTION"""
        session_id = data.get('sessionId') or data.get('session_id') or data.get('sessionid')
        logger.info(f"🚀 ===== joinInterview EVENT TRIGGERED =====")
        logger.info(f"   Session ID: {session_id}, Socket SID: {request.sid}")
        
        try:
            # ✅ CRITICAL: Load existing session from store
            session = session_store.get(session_id)
            
            if not session:
                logger.error(f"❌ Session {session_id} not found in store!")
                emit('error', {'message': 'Session not found. Please restart the interview.'}, room=request.sid)
                return {'status': 'error', 'message': 'Session not found'}

            # 🛑 ZOMBIE KILLER - CRITICAL FIX
            if getattr(session, 'interview_ended', False):
                logger.warning(f"🧟 Zombie Reconnection detected for ended session {session_id}. Redirecting...")
                emit('interviewComplete', {
                    'completed': True,
                    'message': 'Interview already completed. Redirecting to results...',
                    'session_id': session_id,
                    'questions_asked': getattr(session, 'question_count', 0)
                }, room=session_id)
                return {'status': 'ended'}
            # 🛑 ZOMBIE KILLER END

            logger.info(f"✅ Loaded session: {session.session_id}, interview_id={session.interview_id}")
            logger.info(f"   Job: {session.job_title}, Questions: {session.question_count}")
            
            # Update speech mode if provided
            speech_mode = data.get('speech_mode', 'browser')
            session.speech_mode = speech_mode
            
            # Join socket room
            join_room(session_id)
            
            # ✅ CRITICAL: Map socket SID to session for disconnect cleanup
            sid_to_session[request.sid] = session_id
            logger.info(f"✅ Mapped socket SID {request.sid} → session {session_id}")
            
            # Get first question (already generated during /start)
            first_question = session.current_question
            
            if not first_question:
                logger.warning("⚠️ No current_question in session, generating new one")
                try:
                    question_service = QuestionService()
                    first_question = question_service.generate_first_question(session)
                    session.current_question = first_question
                    session_store.add(session)  # Save updated session
                except Exception as q_error:
                    logger.error(f"❌ Failed to generate first question: {q_error}", exc_info=True)
                    first_question = "Tell me about yourself and why you're interested in this position."
                    session.current_question = first_question
                    session_store.add(session)
            
            # Send question to frontend - use both room and direct emit for reliability
            try:
                emit('question', {
                    'question': first_question,
                    'question_number': 1  # ✅ Consistent snake_case
                }, room=session_id)
                
                emit('aiSpeaking', {
                    'question': first_question,
                    'is_speaking': True,
                    'question_number': 1,
                    'is_final': False
                }, room=session_id)
                logger.info(f"✅ Events emitted successfully for {session_id}")
            except Exception as emit_error:
                logger.error(f"❌ Failed to emit events: {emit_error}", exc_info=True)
                # Try direct emit as fallback
                try:
                    socketio.emit('question', {
                        'question': first_question,
                        'question_number': 1
                    }, room=session_id)
                    socketio.emit('aiSpeaking', {
                        'question': first_question,
                        'is_speaking': True,
                        'question_number': 1,
                        'is_final': False
                    }, room=session_id)
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback emit also failed: {fallback_error}")
            
            logger.info(f"✅ joinInterview COMPLETED - Question sent: '{first_question[:50]}...'")
            return {'status': 'ok'}
            
        except Exception as e:
            logger.error(f"❌ joinInterview failed: {e}", exc_info=True)
            try:
                emit('error', {'message': 'Failed to join interview'}, room=request.sid)
            except:
                pass
            return {'status': 'error', 'message': str(e)}

    @socketio.on('startRecording')
    def handle_start_recording(data):
        """Handle recording start - Non-Blocking + Buffer Flushing"""
        session_id = data.get('sessionId') or data.get('sessionid') or data.get('session_id')

        session = session_store.get(session_id)
        if not session:
            emit('error', {'message': 'Session not found'})
            return {'status': 'error', 'message': 'Session not found'}

        # --- BACKGROUND TASK ---
        def start_transcription_bg(sid):
            try:
                if transcription_service and transcription_service.initialized:
                    logger.info(f"🎤 Starting Azure streaming in background for {sid}")
                    
                    # 1. Connect to Azure (This takes 1-3 seconds)
                    success = transcription_service.start_streaming(sid, socketio, room=sid)
                    
                    if success:
                        logger.info(f"✅ Azure connected for {sid}. Flushing buffer...")
                        
                        # 2. FLUSH BUFFER: Send any audio chunks that arrived while connecting
                        if sid in pending_audio_buffers:
                            for chunk in pending_audio_buffers[sid]:
                                transcription_service.push_audio_chunk(sid, chunk)
                            logger.info(f"🚀 Flushed {len(pending_audio_buffers[sid])} buffered chunks for {sid}")
                            del pending_audio_buffers[sid] # Clear memory
                        
                        # 3. Notify Frontend
                        socketio.emit('recordingStarted', {
                            'session_id': sid,
                            'transcription_enabled': True,
                            'provider': 'azure_speech_service'
                        }, room=sid, namespace='/')
                    else:
                        logger.error(f"❌ Failed to start streaming for {sid}")
            except Exception as e:
                logger.error(f"❌ Error in background transcription start: {e}")

        # --- MAIN LOGIC ---
        if session and session.speech_mode == 'server':
            if transcription_service and transcription_service.initialized:
                # Initialize buffer for this session
                pending_audio_buffers[session_id] = []
                
                # 🚀 Run connection in background so we don't block the PING heartbeat
                eventlet.spawn(start_transcription_bg, session_id)
                
                return {'status': 'pending_transcription'}
            else:
                emit('recordingStarted', {
                    'session_id': session_id,
                    'transcription_enabled': False,
                    'provider': 'none'
                }, room=session_id)
                return {'status': 'ok', 'transcription_enabled': False}
        else:
            emit('recordingStarted', {
                'session_id': session_id,
                'transcription_enabled': False,
                'provider': 'browser'
            }, room=session_id)
            return {'status': 'ok'}

    @socketio.on('videoChunk')
    def handle_video_chunk(data, callback=None):
        """Handle video chunks - matches frontend event name"""
        session_id = data.get('sessionId')
        chunk_number = data.get('chunkNumber')
        binary_data = data.get('data')

        session = session_store.get(session_id)
        if not session:
            logger.warning(f"Video chunk for unknown session: {session_id}")
            if callback:
                callback({'ok': False, 'message': 'Session not found'})
            return

        if not binary_data or (hasattr(binary_data, '__len__') and len(binary_data) == 0):
            logger.warning("Empty video chunk received")
            if callback:
                callback({'ok': False, 'message': 'Empty data'})
            return

        try:
            recording_service = RecordingService()
            success = tpool.execute(recording_service.save_video_chunk, session_id, binary_data)
            if success:
                logger.debug(f"✅ Video chunk {chunk_number} saved")
                if callback:
                    callback({'ok': True})
            else:
                logger.error(f"❌ Failed to save video chunk {chunk_number}")
                if callback:
                    callback({'ok': False})

        except Exception as e:
            logger.error(f"❌ Error handling video chunk: {e}", exc_info=True)
            if callback:
                callback({'ok': False, 'message': str(e)})

    @socketio.on('audioChunk')
    def handle_audio_chunk(data, callback=None):
        """Handle audio chunks - With Buffering to prevent data loss"""
        session_id = data.get('sessionId')
        chunk_number = data.get('chunkNumber')
        binary_data = data.get('data')

        session = session_store.get(session_id)
        if not session:
            logger.warning(f"⚠️ Audio chunk for unknown session: {session_id}")
            if callback:
                callback({'ok': False, 'message': 'Session not found'})
            return

        if not binary_data or (hasattr(binary_data, '__len__') and len(binary_data) == 0):
            logger.warning("⚠️ Empty audio chunk received")
            if callback:
                callback({'ok': False, 'message': 'Empty data'})
            return

        try:
            recording_service = RecordingService()
            
            # 1. SAVE TO DISK (Threaded)
            tpool.execute(recording_service.save_audio_chunk, session_id, binary_data)

            # 2. HANDLE TRANSCRIPTION FLOW
            if session and session.speech_mode == 'server' and transcription_service and transcription_service.initialized:
                
                # Check if the Azure stream is already fully connected
                if session_id in transcription_service.active_streams:
                    # ✅ Case A: Connected. Send directly.
                    transcription_service.push_audio_chunk(session_id, binary_data)
                
                # If not connected yet, check if we are waiting for connection (Buffering)
                elif session_id in pending_audio_buffers:
                    # ⏳ Case B: Connecting... Buffer the data!
                    pending_audio_buffers[session_id].append(binary_data)
                
                else:
                    # Case C: Not active and not in buffer
                    pass

            if callback:
                callback({'ok': True})
                
        except Exception as e:
            logger.error(f"❌ Error handling audio chunk: {e}", exc_info=True)
            if callback:
                callback({'ok': False, 'message': str(e)})
                
    @socketio.on('stopRecording')
    def handle_stop_recording(data):
        """Handle recording stop - now with finalization"""
        session_id = data.get('sessionId') or data.get('sessionid') or data.get('session_id')
        session = session_store.get(session_id)
        
        if not session:
            emit('error', {'message': 'Session not found'})
            return {'status': 'error'}
        
        # Stop transcription if active
        final_transcript = ""
        if session and session.speech_mode == 'server':
            if transcription_service and transcription_service.initialized:
                final_transcript = transcription_service.stop_streaming(session_id)
                if final_transcript:
                    session.full_transcript.append(final_transcript)
                    session_store.add(session)
                    logger.info(f"📝 Final transcript saved ({len(final_transcript)} chars)")
        
        # Close file handles
        recording_service = RecordingService()
        recording_service.close_recordings(session_id)
        
        # ✅ CRITICAL: Finalize recordings immediately
        logger.info("🔧 Finalizing recordings...")
        finalization_results = {
            'video_finalized': False,
            'audio_finalized': False
        }
        
        if session.video_file and os.path.exists(session.video_file):
            finalization_results['video_finalized'] = recording_service.finalize_recording(session.video_file)
        
        if session.audio_file and os.path.exists(session.audio_file):
            finalization_results['audio_finalized'] = recording_service.finalize_recording(session.audio_file)
        
        emit('recordingStopped', {
            'session_id': session_id,
            'final_transcript': final_transcript,
            'transcript_length': len(final_transcript),
            'recordings_finalized': finalization_results
        }, room=session_id)

    @socketio.on('finishSpeaking')
    def handle_finish_speaking(data):
        session_id = data.get('sessionId') or data.get('sessionid') or data.get('session_id')
        answer = (data.get('answer') or '').strip()
        
        logger.info("=" * 70)
        logger.info("🗣️ finishSpeaking EVENT TRIGGERED")
        logger.info(f"📥 Received: session={session_id}, answer='{answer[:50]}...'")
        
        try:
            # 1. Fetch Session (Main Thread)
            session = session_store.get(session_id)
            if not session:
                emit('error', {'message': 'Session not found'}, room=session_id)
                return
            
            if getattr(session, 'interview_ended', False):
                logger.info(f"⛔ Interview {session_id} already ended")
                return

            if len(answer) < 2:
                answer = "[No verbal response detected]"
            
            # ✅ STEP 1: Save answer & Increment Count (AUTHORITATIVE UPDATE)
            session.add_exchange(session.current_question, answer)
            
            # Update the count here. This is now the "Official" count for the NEXT question.
            # Example: Finished Q1. Count becomes 2. Next question is Q2.
            session.question_count += 1 
            
            session_store.add(session) # Save to DB
            
            logger.info(f"✅ Q{session.question_count - 1} Answered | Moving to Q{session.question_count}")

            # ✅ STEP 2: Send confirmation to frontend
            emit('answer_received', {
                'success': True, 
                'answer_length': len(answer),
                'question_count': session.question_count 
            }, room=session_id)
            
            # 🛑 CHECK LIMIT
            if session.question_count > MAXQUESTIONS:
                logger.info(f"🏁 MAX REACHED: {session.question_count - 1}/{MAXQUESTIONS}")
                closing_message = "Thank you! Interview complete."
                emit('aiSpeaking', {
                    'question': closing_message,
                    'is_speaking': True,
                    'question_number': session.question_count,
                    'is_final': True
                }, room=session_id)
                return

            # ✅ STEP 3: Generate next question
            # 🔥 CRITICAL FIX: Pass the 'session' OBJECT, not just the ID.
            # This ensures the background thread uses the memory version which DEFINITELY has the answer.
            eventlet.spawn(safe_generate_question, socketio, session, answer)
            
        except Exception as e:
            logger.error(f"❌ handle_finish_speaking failed: {e}", exc_info=True)
            emit('error', {'message': 'Failed to process answer'}, room=session_id)

    def safe_generate_question(socketio, current_session, answer):
        """Background task: Generate next question (NAMESPACE FIXED)"""
        try:
            session_id = current_session.session_id
            logger.info(f"🤖 [BG] Generating next question for session {session_id}")
            
            # Generate next question
            question_service = QuestionService()
            next_question = question_service.generate_next_question(current_session, answer)
            
            # Validate
            if not next_question or len(next_question.strip()) < 5:
                logger.warning("⚠️ [BG] Generated question too short, using fallback")
                next_question = "Tell me about a recent project you're proud of."
            
            # Update session
            current_session.current_question = next_question
            session_store.add(current_session)
            
            display_number = current_session.question_count
            
            logger.info(f"✅ [BG] Generated Q{display_number}: '{next_question[:50]}...'")
            
            # ✅ CRITICAL FIX: Add namespace='/' for background thread emits
            socketio.emit('question', {
                'question': next_question,
                'question_number': display_number
            }, room=session_id, namespace='/')
            
            socketio.emit('aiSpeaking', {
                'question': next_question,
                'is_speaking': True,
                'question_number': display_number,
                'is_final': False
            }, room=session_id, namespace='/')
            
            logger.info(f"✅ [BG] Successfully emitted Q{display_number} to room {session_id}")
            
        except Exception as e:
            logger.error(f"❌ [BG] FAILED to generate question: {e}", exc_info=True)
            
            try:
                fallback_num = current_session.question_count if current_session else 0
                fallback_msg = "Tell me about a challenge you overcame."
                
                # ✅ FIXED: Add namespace to fallback emits
                socketio.emit('question', {
                    'question': fallback_msg,
                    'question_number': fallback_num
                }, room=current_session.session_id, namespace='/')
                
                socketio.emit('aiSpeaking', {
                    'question': fallback_msg,
                    'is_speaking': True,
                    'question_number': fallback_num,
                    'is_final': False
                }, room=current_session.session_id, namespace='/')
            except Exception as fallback_error:
                logger.error(f"❌ [BG] Even fallback failed: {fallback_error}")

    @socketio.on('endInterview')
    def handle_end_interview(data):
        session_id = data.get('sessionId') or data.get('sessionid') or data.get('session_id')
        logger.info(f"🏁 Interview END requested: {session_id}")
        
        try:
            session = session_store.get(session_id)
            if not session:
                emit('interviewComplete', {
                    'completed': True,
                    'message': 'Interview ended',
                    'questions_asked': 0
                }, room=session_id)
                return
            
            # Mark as ended
            session.interview_ended = True
            session_store.add(session)
            
            # Close recordings
            recording_service = RecordingService()
            recording_service.close_recordings(session_id)
            
            # ✅ UPDATE DATABASE - This is where magic happens
            try:
                from application.data.models import Interview
                from application.data.database import db
                
                interview = Interview.query.get(session.interview_id)
                if interview:
                    interview.interview_recording_url = f"/static/recordings/{session_id}/video.mp4"
                    interview.status = "completed"  # ✅ STATUS UPDATE
                    db.session.commit()
                    logger.info(f"✅ Updated Interview #{session.interview_id}: status=completed, recording_url saved")
                else:
                    logger.warning(f"⚠️ Interview ID {session.interview_id} not found in database")
            except Exception as e:
                logger.error(f"❌ Failed to update Interview table: {e}", exc_info=True)
            
            # Emit completion
            emit('interviewComplete', {
                'completed': True,
                'message': 'Interview submitted successfully.',
                'session_id': session_id,
                'questions_asked': len(session.conversation_history),
                'processing_status': 'background'
            }, room=session_id)
            
            logger.info(f"🚀 Client released. Starting background tasks for {session_id}")
            eventlet.spawn(_background_processing, session_id)
            
        except Exception as e:
            logger.error(f"❌ endInterview error: {e}", exc_info=True)
            emit('interviewComplete', {'completed': True, 'error': str(e)}, room=session_id)

    # ✅ Keep-alive ping handler
    @socketio.on('ping')
    def handle_ping(data):
        """Handle keep-alive ping from client"""
        session_id = sid_to_session.get(request.sid)
        if session_id:
            # Just acknowledge - keeps connection alive
            emit('pong', {'timestamp': data.get('timestamp')}, room=request.sid)
            logger.debug(f"💓 Ping received from {request.sid} (session: {session_id})")

    # ✅ FIXED: Enhanced disconnect with PROPER session_id mapping
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnect - FULL RESOURCE CLEANUP"""
        sid = request.sid
        session_id = sid_to_session.pop(sid, None)  # ✅ Get session_id or None
        
        logger.info(f"👋 Client {sid} disconnected")
        
        try:
            if session_id and transcription_service and transcription_service.initialized:
                if session_id in transcription_service.active_streams:
                    logger.info(f"🧹 Cleaning Azure stream for session {session_id}")
                    transcription_service.stop_streaming(session_id)
                
                if session_id in pending_audio_buffers:
                    logger.info(f"🧹 Cleared {len(pending_audio_buffers[session_id])} buffered chunks for {session_id}")
                    del pending_audio_buffers[session_id]
                    
        except Exception as e:
            logger.error(f"❌ Disconnect cleanup failed for {sid}: {e}")

    logger.info("✅ Socket.IO handlers registered - 100% PRODUCTION READY:")
    logger.info("   📌 joinInterview ✅ ZOMBIE-PROOF + SID MAPPING")
    logger.info("   📌 startRecording ✅ FIXED")
    logger.info("   📌 stopRecording ✅ FIXED")
    logger.info("   📌 finishSpeaking ✅ FIXED")
    logger.info("   📌 videoChunk ✅ FIXED")
    logger.info("   📌 audioChunk ✅ FIXED")
    logger.info("   📌 endInterview ✅ FIXED")
    logger.info("   📌 disconnect ✅ FULL CLEANUP")
    logger.info("=" * 70)

# ✅ No return needed - decorators handle registration

