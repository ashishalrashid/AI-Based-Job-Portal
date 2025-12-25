"""
Recording Service - Handles file I/O for video/audio recording
"""
import os
import logging
import json
import subprocess
from typing import Optional
from threading import Lock

# ✅ CRITICAL FIX: Cross-platform import
# This prevents the app from crashing on Windows
try:
    import fcntl
    HAS_OS_LOCKING = True
except ImportError:
    HAS_OS_LOCKING = False  # Windows fallback

logger = logging.getLogger(__name__)

# File locks per session to prevent concurrent writes
_file_locks = {}
_locks_lock = Lock()

def _get_file_lock(session_id: str) -> Lock:
    """Get or create a lock for this session's files"""
    with _locks_lock:
        if session_id not in _file_locks:
            _file_locks[session_id] = Lock()
        return _file_locks[session_id]


class RecordingService:
    """Handles all recording and file operations with per-chunk I/O"""

    def save_video_chunk(self, session_id: str, video_bytes: bytes) -> bool:
        """Save video chunk to file (append mode) with Safe Locking"""
        from ..models.session_store import get_session

        session = get_session(session_id)
        if not session:
            logger.error(f"❌ No session found for {session_id}")
            return False
        
        if not session.video_file or not session.recording_path:
            logger.error(f"❌ Paths missing for session {session_id}")
            return False

        lock = _get_file_lock(session_id)
        try:
            with lock:  # ✅ THREAD LOCK (Works on Windows & Linux)
                with open(session.video_file, 'ab') as f:
                    # ✅ OS LOCK (Only runs on Linux/Mac)
                    if HAS_OS_LOCKING:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    
                    f.write(video_bytes)
                    
                    if HAS_OS_LOCKING:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            # Reduce log noise: change to debug
            # logger.debug(f"✅ Video chunk saved") 
            return True
        except Exception as e:
            logger.error(f"❌ Error saving video chunk for {session_id}: {e}", exc_info=True)
            return False

    def save_audio_chunk(self, session_id: str, audio_bytes: bytes) -> bool:
        """Save audio chunk to file (append mode) with Safe Locking"""
        from ..models.session_store import get_session

        session = get_session(session_id)
        if not session or not session.audio_file:
            logger.warning(f"Cannot save audio chunk: session or audio_file missing for {session_id}")
            return False

        lock = _get_file_lock(session_id)
        try:
            with lock:  # ✅ THREAD LOCK
                with open(session.audio_file, 'ab') as f:
                    if HAS_OS_LOCKING:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    
                    f.write(audio_bytes)
                    f.flush()
                    os.fsync(f.fileno()) # ✅ EXTRA SAFETY
                    
                    if HAS_OS_LOCKING:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return True
        except Exception as e:
            logger.error(f"❌ Error saving audio chunk for {session_id}: {e}", exc_info=True)
            return False

    def close_recordings(self, session_id: str):
        """Logical close for recordings. Removes lock associated with the session."""
        with _locks_lock:
            if session_id in _file_locks:
                del _file_locks[session_id]
                logger.info(f"📹 Recordings closed and locks cleaned for {session_id}")

    def save_transcript(self, session) -> bool:
        """Save interview transcript as text file"""
        if not session.recording_path:
            logger.error(f"Transcript save failed: recording_path missing for session {session.session_id}")
            return False
        
        from ..utils.file_utils import safe_write_file
        
        transcript_path = os.path.join(session.recording_path, "transcript.txt")
        # Join with double newline for readability
        transcript_text = "\n\n".join(session.full_transcript)
        
        success = safe_write_file(transcript_path, transcript_text)
        if success:
            logger.info(f"Transcript saved: {transcript_path}")
        else:
            logger.error(f"Failed to save transcript: {transcript_path}")
        
        return success


    def save_evaluation(self, session, evaluation: dict) -> bool:
        """Save evaluation JSON file"""
        if not session.recording_path:
            return False

        eval_path = os.path.join(session.recording_path, 'evaluation.json')

        try:
            with open(eval_path, 'w', encoding='utf-8') as f:
                json.dump(evaluation, f, indent=2, ensure_ascii=False)
            logger.info(f"📊 Evaluation saved: {eval_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save evaluation: {e}")
            return False

    def save_metadata(self, session, evaluation) -> bool:
        """Save interview metadata JSON file"""
        if not session.recording_path:
            logger.error(f"Metadata save failed: recording_path missing for session {session.session_id}")
            return False

        # Safely get candidate name (defaults to 'Unknown' if missing)
        candidate_name = session.candidate_background.get('name', 'Unknown') if getattr(session, 'candidate_background', None) else 'Unknown'

        # Handle evaluation safely when it might be a string or dict
        if isinstance(evaluation, dict):
            overall_rating = evaluation.get("overall_rating", 0)
            rec = evaluation.get("recommendation")
            if isinstance(rec, dict):
                recommendation = rec.get("decision", "Unknown")
            else:
                recommendation = "Unknown"
        else:
            # Covers str, None, or malformed evaluation object
            overall_rating = 0
            recommendation = "Unknown"

        metadata = {
            "session_id": session.session_id,
            "interview_id": session.interview_id,
            "job_title": session.job_title,
            "candidate_name": candidate_name,
            "started_at": session.started_at.isoformat(),
            "duration_minutes": getattr(session, 'get_duration_minutes', lambda: 0)(),
            "questions_asked": len(getattr(session, 'conversation_history', [])),
            "topics_covered": list(getattr(session, 'topics_covered', [])),
            "detected_level": getattr(session, 'candidate_expertise_level', "unknown"),
            "overall_rating": overall_rating,
            "recommendation": recommendation,
        }

        metadata_path = os.path.join(session.recording_path, 'metadata.json')

        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"📋 Metadata saved: {metadata_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {e}")
            return False


    def get_video_path(self, session_id: str) -> Optional[str]:
        """Get video file path"""
        from ..models.session_store import get_session
        session = get_session(session_id)
        if session and session.video_file and os.path.exists(session.video_file):
            return session.video_file
        return None
    
    def finalize_recording(self, file_path: str) -> bool:
        """
        Runs FFmpeg to REPAIR and TRANSCODE the stream.
        - Converts Variable Frame Rate (VFR) to Constant (CFR) to fix freezing [web:5]
        - Converts WebM to MP4 for maximum compatibility [web:6]
        - Resamples audio to fix drift [web:7]
        """
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"⚠️ Cannot finalize missing file: {file_path}")
            return False

        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        raw_path = os.path.join(directory, f"raw_{filename}")
        
        # Output to MP4 for better stability and compatibility
        final_mp4_path = file_path.replace('.webm', '.mp4')
        
        # Check file size before processing
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        logger.info(f"📦 Finalizing {filename} ({file_size_mb:.2f} MB)")
        
        try:
            # 1. Rename current (potentially glitchy) file to "raw_"
            os.rename(file_path, raw_path)
            
            # 2. Build the repair command
            command = ['ffmpeg', '-y', '-i', raw_path]

            # Detect if this is video or audio file based on filename
            is_video_file = 'video' in filename.lower()

            if is_video_file:
                # === VIDEO REPAIR STRATEGY ===
                command.extend([
                    '-r', '30',                     # Force Constant 30 FPS (Fixes frozen frames)
                    '-c:v', 'libx264',              # Encode to H.264 (Standard MP4 video)
                    '-preset', 'fast',              # Fast encoding
                    '-crf', '23',                   # High Quality (lower = better, 23 is recommended)
                    '-pix_fmt', 'yuv420p',          # Ensure compatibility with all players
                    '-movflags', 'faststart',       # Web Optimization
                    '-c:a', 'aac',                  # AAC Audio (Standard)
                    '-b:a', '128k'                  # Good audio bitrate
                ])
            else:
                # === AUDIO REPAIR STRATEGY ===
                command.extend([
                    '-vn',                          # No video
                    '-c:a', 'aac',                  # Re-encode to AAC (Fixes choppy audio)
                    '-b:a', '128k'
                ])

            # === AUDIO SYNC FIX ===
            # aresample=async=1: Fixes timestamps if audio drifted from video
            command.extend(['-af', 'aresample=async=1', final_mp4_path])
            
            logger.info(f"🔧 Transcoding/Repairing: {raw_path} -> {final_mp4_path}")
            
            # 3. Run FFmpeg (Increased timeout - transcoding is slower than copying)
            result = subprocess.run(
                command, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=300  # 5 minutes timeout
            )
            
            # 4. Verify output
            if os.path.exists(final_mp4_path) and os.path.getsize(final_mp4_path) > 0:
                fixed_size_mb = os.path.getsize(final_mp4_path) / (1024 * 1024)
                logger.info(f"✅ File finalized: {os.path.basename(final_mp4_path)} ({fixed_size_mb:.2f} MB)")
                
                # Cleanup raw file
                os.remove(raw_path)
                
                return True
            else:
                raise Exception("FFmpeg output file is empty or missing")
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ FFmpeg timeout after 300s for {filename}")
            # Restore raw file so we don't lose data
            if os.path.exists(raw_path):
                os.rename(raw_path, file_path)
            return False
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"❌ FFmpeg failed: {error_msg}")
            # Restore original if repair failed
            if os.path.exists(raw_path):
                os.rename(raw_path, file_path)
            return False
            
        except Exception as e:
            logger.error(f"❌ Error finalizing recording: {e}", exc_info=True)
            # Restore original
            if os.path.exists(raw_path) and not os.path.exists(file_path):
                os.rename(raw_path, file_path)
            return False

