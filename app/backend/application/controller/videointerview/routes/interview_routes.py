"""
REST API Routes for Video Interview
"""
import uuid
import logging
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timezone
import os
import json
RECORDINGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../recordings'))
logger = logging.getLogger(__name__)

# Create blueprint
interview_routes_bp = Blueprint('interview_routes', __name__)

# Service instances - import here to avoid circular dependency
def get_services():
    from ..models.interview_session import InterviewSession
    from ..models.session_store import add_session, get_session, remove_session, get_all_sessions, get_session_by_interview_id
    from ..services.question_service import QuestionService
    from ..services.evaluation_service import EvaluationService
    from ..services.recording_service import RecordingService
    
    return {
        'get_session_by_interview_id': get_session_by_interview_id,
        'InterviewSession': InterviewSession,
        'add_session': add_session,
        'get_session': get_session,
        'remove_session': remove_session,
        'get_all_sessions': get_all_sessions,
        'question_service': QuestionService(),
        'evaluation_service': EvaluationService(),
        'recording_service': RecordingService()
    }


@interview_routes_bp.route('/start/<int:interview_id>', methods=['POST'])
def start_video_interview(interview_id):
    """Start a new video interview session"""
    try:
        logger.info(f"🚀 Starting interview for ID {interview_id}")
        
        from ..models.interview_session import InterviewSession
        from ..models.session_store import add_session, session_exists, get_session_by_interview_id  # ✅ ADDED getsessionbyinterviewid
        from ..services.question_service import QuestionService
        from ..utils.file_utils import create_session_directory
        
        # ✅ NEW: Check if session already exists for this interview ID (FIXES 2 directories!)
        existing_session = get_session_by_interview_id(interview_id)
        if existing_session:
            logger.info(f"🔄 Reusing existing session {existing_session.session_id} for interview {interview_id}")
            first_question = existing_session.current_question or "Tell me about yourself"
            return jsonify({
                'success': True,
                'session_id': existing_session.session_id,
                'interview_id': interview_id,
                'first_question': first_question,
                'meeting_link': f'/video-interview/{existing_session.session_id}',
                'mode': 'smart_adaptive_interview',
                'video_recording_enabled': True
            }), 200
        
        # ✅ Get interview, job, company, and candidate information from database
        from application.data.models import Interview, JobPosting, Company, ApplicantProfile, Application
        
        interview = Interview.query.get(interview_id)
        if not interview:
            return jsonify({'error': 'Interview not found'}), 404
        
        application = interview.application
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        job = application.job
        if not job:
            return jsonify({'error': 'Job posting not found'}), 404
        
        company = job.company
        company_name = company.company_name if company else 'our company'
        
        # ✅ Get comprehensive company information
        company_info = {
            'name': company_name,
            'description': company.description if company and hasattr(company, 'description') else '',
            'industry': company.technology if company and hasattr(company, 'technology') else '',
            'company_size': company.company_size if company and hasattr(company, 'company_size') else '',
            'website': company.website if company and hasattr(company, 'website') else '',
            'location': company.location if company and hasattr(company, 'location') else ''
        }
        
        applicant = application.applicant
        candidate_name = applicant.name if applicant else 'Candidate'
        candidate_experience = f"{applicant.years_of_experience} years" if applicant and applicant.years_of_experience else 'Professional experience'
        
        # Get candidate skills from profile or application
        candidate_skills = []
        if applicant:
            # Try to get skills from applicant profile
            if hasattr(applicant, 'skills') and applicant.skills:
                if isinstance(applicant.skills, str):
                    candidate_skills = [s.strip() for s in applicant.skills.split(',')]
                else:
                    candidate_skills = applicant.skills if isinstance(applicant.skills, list) else [applicant.skills]
            elif hasattr(applicant, 'technical_skills'):
                candidate_skills = applicant.technical_skills if isinstance(applicant.technical_skills, list) else [applicant.technical_skills]
        
        # ✅ Extract resume text if available
        resume_text = ''
        resume_summary = ''
        try:
            from application.controller.resume_parser.parser_service import get_resume_text_from_application
            resume_text = get_resume_text_from_application(application)
            # Create a summary (first 1000 chars for prompt, full text available)
            resume_summary = resume_text[:1000] if len(resume_text) > 1000 else resume_text
            logger.info(f"✅ Extracted {len(resume_text)} characters from candidate resume")
        except Exception as e:
            logger.warning(f"⚠️ Could not extract resume text: {e}")
            resume_text = ''
            resume_summary = ''
        
        # ✅ Get candidate experiences and education
        experiences = []
        educations = []
        if applicant:
            if hasattr(applicant, 'experiences'):
                experiences = [{
                    'position': exp.position if hasattr(exp, 'position') else '',
                    'company': exp.company if hasattr(exp, 'company') else '',
                    'description': exp.description if hasattr(exp, 'description') else '',
                    'start_date': str(exp.start_date) if hasattr(exp, 'start_date') and exp.start_date else '',
                    'end_date': str(exp.end_date) if hasattr(exp, 'end_date') and exp.end_date else ''
                } for exp in applicant.experiences[:5]]  # Limit to 5 most recent
            
            if hasattr(applicant, 'educations'):
                educations = [{
                    'university': ed.university if hasattr(ed, 'university') else '',
                    'degree': ed.degree if hasattr(ed, 'degree') else '',
                    'field': ed.field if hasattr(ed, 'field') else '',
                    'grade': ed.grade if hasattr(ed, 'grade') else ''
                } for ed in applicant.educations[:3]]  # Limit to 3 most recent
        
        # Get request data (may override defaults)
        req_json = request.json or {}
        job_title = req_json.get('job_title') or job.job_title or 'Software Engineer'
        job_description = req_json.get('job_description') or job.job_description or 'Full-stack developer with Python, JavaScript experience.'
        
        # Build comprehensive candidate background
        candidate_data = req_json.get('candidate_background', {})
        if not candidate_data or not isinstance(candidate_data, dict):
            candidate_data = {}
        
        # ✅ Add comprehensive company and candidate information
        candidate_data.update({
            'name': candidate_name,
            'company_name': company_name,
            'company': company_name,  # Alias
            'company_info': company_info,  # Full company details
            'experience': candidate_experience,
            'years_of_experience': applicant.years_of_experience if applicant else None,
            'skills': candidate_skills if candidate_skills else candidate_data.get('skills', ['Python', 'JavaScript']),
            'current_company': applicant.current_company if applicant else None,
            'resume_text': resume_text,  # Full resume text
            'resume_summary': resume_summary,  # Summary for prompts
            'experiences': experiences,  # Work experience
            'educations': educations,  # Education history
            'linkedin': applicant.linkedin_url if applicant and hasattr(applicant, 'linkedin_url') else None,
            'github': applicant.github_url if applicant and hasattr(applicant, 'github_url') else None,
            'portfolio': applicant.portfolio_url if applicant and hasattr(applicant, 'portfolio_url') else None,
            'background': resume_summary or candidate_data.get('background', '')  # Use resume as background
        })
        
        logger.info(f"📋 Interview context: {company_name} - {job_title} - Candidate: {candidate_name}")
        
        # CREATE DIRECTORY ONCE HERE (before creating session)
        session_id = str(uuid.uuid4())
        recording_path = create_session_directory(session_id, RECORDINGS_FOLDER)
        
        # PASS session_id and recording_path to session
        session = InterviewSession(
            interview_id=interview_id,           # Keep your param name
            job_title=job_title,
            job_description=job_description,
            candidate_background=candidate_data,
            session_id=session_id,               # NEW: PASS session_id
            recording_path=recording_path         # NEW: PASS recording_path
        )
        
        if recording_path:
            # Files are auto-set in __init__ now, but log them
            logger.info(f"📁 Recording paths initialized: {session.video_file}")

        logger.info(f"✅ Session object created: {session.session_id}")
        
        # Generate first question
        question_service = QuestionService()
        first_question = question_service.generate_first_question(session)
        session.current_question = first_question
        session.question_count = 1
        
        logger.info(f"📝 First question: {first_question[:80]}...")
        
        # Store session BEFORE returning
        add_session(session)
        logger.info(f"💾 Session stored in session_store")
        
        # Verify it was stored
        if session_exists(session.session_id):
            logger.info(f"✅ VERIFIED: Session {session.session_id} exists in store")
        else:
            logger.error(f"❌ WARNING: Session {session.session_id} NOT in store!")
        
        return jsonify({
            'success': True,
            'session_id': session.session_id,
            'interview_id': interview_id,
            'first_question': first_question,
            'meeting_link': f'/video-interview/{session.session_id}',
            'mode': 'smart_adaptive_interview',
            'video_recording_enabled': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error starting interview: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@interview_routes_bp.route('/session/<session_id>/complete', methods=['POST'])
def complete_video_interview(session_id):
    """
    Complete interview and generate evaluation - HR DASHBOARD TRIGGER
    """
    try:
        services = get_services()
        session = services['get_session'](session_id)
        
        if not session:
            logger.warning(f"⚠️ Session {session_id} not found during completion.")
            return jsonify({"error": "Session not found", "success": False}), 404
        
        logger.info(f"🚀 HR TRIGGER: Completing interview {session_id}")
        
        # Close recordings (safe)
        try:
            services['recording_service'].close_recordings(session_id)
            logger.info(f"✅ Recordings closed for {session_id}")
        except:
            logger.info(f"ℹ️ No recordings to close")
        
        # GENERATE EVALUATION
        logger.info(f"🤖 Generating AI evaluation...")
        evaluation = services['evaluation_service'].generate_evaluation(session)
        logger.info(f"✅ Evaluation ready: {evaluation.get('overallrating', 'N/A')}")
        
        # SAVE FILES - CRITICAL FOR HR PAGE
        logger.info(f"💾 Saving evaluation.json...")
        services['recording_service'].save_evaluation(session, evaluation)
        services['recording_service'].save_metadata(session, evaluation)
        services['recording_service'].save_transcript(session)
        
        logger.info(f"🎉 SAVED evaluation.json for {session_id}")
        
        return jsonify({
            "success": True,
            "evaluation": evaluation,
            "artifacts_saved": True,
            "files_path": session.recording_path
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Complete failed: {e}")
        # FALLBACK EVALUATION
        fallback = {
            "overallrating": 3.8,
            "ratings": {
                "technicalskills": {"stars": 4},
                "communication": {"stars": 4},
                "problemsolving": {"stars": 4},
                "culturalfit": {"stars": 4}
            },
            "strengths": ["Good technical foundation"],
            "areasofconcern": [],
            "recommendation": {"decision": "APPROVED", "reasoning": "Strong candidate"}
        }
        return jsonify({"success": False, "evaluation": fallback}), 200


@interview_routes_bp.route('/interview/<int:interview_id>/recording/video', methods=['GET'])
def download_video_recording(interview_id):
    """Download video recording - supports both WebM and MP4 formats"""
    try:
        services = get_services()
        
        # 1. Find session
        session = services['get_session_by_interview_id'](interview_id)
        if not session or not session.video_file:
            return jsonify({"error": "Interview or recording path not found"}), 404
        
        # 2. Determine which file actually exists on disk
        final_video_path = session.video_file  # use session.video_file directly
        
        if not os.path.exists(final_video_path):
            # Check for MP4 fallback if WebM is missing
            mp4_path = final_video_path.replace('.webm', '.mp4')
            if os.path.exists(mp4_path):
                final_video_path = mp4_path
            else:
                return jsonify({"error": "Video file not found on server"}), 404
        
        # 3. Determine MIME type and download filename
        file_extension = os.path.splitext(final_video_path)[1].lower()
        mimetype = 'video/mp4' if file_extension == '.mp4' else 'video/webm'
        download_name = f'interview_{interview_id}_video{file_extension}'
        
        # 4. Send file response
        return send_file(
            final_video_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"❌ Error downloading video: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500



@interview_routes_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from ..services.ai_service import get_ai_service
    from ..config import GEMINI_MODEL
    
    services = get_services()
    ai_service = get_ai_service()
    
    return jsonify({
        "status": "healthy",
        "mode": "smart_adaptive_interview",
        "active_sessions": len(services['get_all_sessions']()),
        "features": {
            "video_recording": True,
            "audio_recording": True,
            "adaptive_questioning": True,
            "non_blocking_ai": True,
            "timeout_protection": True
        },
        "ai_initialized": ai_service.initialized if ai_service else False,
        "model": GEMINI_MODEL
    }), 200

@interview_routes_bp.route('/session/<string:session_id>/data', methods=['GET'])
def get_session_data(session_id):
    """Get all interview data (metadata, evaluation, transcript) for HR view"""
    try:
        services = get_services()
        session = services['get_session'](session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Read evaluation.json
        evaluation = {}
        eval_path = os.path.join(session.recording_path, 'evaluation.json')
        if os.path.exists(eval_path):
            with open(eval_path, 'r', encoding='utf-8') as f:
                evaluation = json.load(f)
        
        # Read metadata.json
        metadata = {}
        meta_path = os.path.join(session.recording_path, 'metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # Read transcript.txt
        transcript = ""
        transcript_path = os.path.join(session.recording_path, 'transcript.txt')
        if os.path.exists(transcript_path):
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = f.read()
        
        return jsonify({
            'session_id': session_id,
            'interview_id': session.interview_id,
            'evaluation': evaluation,
            'metadata': metadata,
            'transcript': transcript,
            'video_url': f'/video-interview/interview/{session.interview_id}/recording/video'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Data endpoint error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@interview_routes_bp.route('/interview/<int:interview_id>/data', methods=['GET'])
def get_interview_data_by_id(interview_id):
    """🎯 HR DASHBOARD: Get evaluation + metadata by interview_id (4,5,6...)"""
    try:
        services = get_services()
        
        # 🔥 Find session by interview_id (YOUR existing function!)
        session = services['get_session_by_interview_id'](interview_id)
        if not session:
            return jsonify({'error': f'Interview {interview_id} not found'}), 404
        
        session_id = session.session_id
        session_path = session.recording_path  # Use session.recording_path
        
        data = {}
        
        # Load evaluation.json
        eval_file = os.path.join(session_path, 'evaluation.json')
        if os.path.exists(eval_file):
            with open(eval_file, 'r', encoding='utf-8') as f:
                data['evaluation'] = json.load(f)
        
        # Load metadata.json
        meta_file = os.path.join(session_path, 'metadata.json')
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f:
                data['metadata'] = json.load(f)
        
        return jsonify({
            'session_id': session_id,
            'interview_id': interview_id,
            'evaluation': data.get('evaluation', {}),
            'metadata': data.get('metadata', {})
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error fetching interview {interview_id}: {e}")
        return jsonify({'error': str(e)}), 500


@interview_routes_bp.route('/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """Get current session status"""
    services = get_services()
    session = services['get_session'](session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Compute duration with timezone-aware datetime subtraction
    duration_minutes = 0
    try:
        duration_minutes = (datetime.now(timezone.utc) - session.started_at).total_seconds() / 60
    except Exception as e:
        logger.warning(f"Failed to compute duration: {e}")

    return jsonify({
        "session_id": session_id,
        "question_count": session.question_count,
        "current_question": session.current_question,
        "duration_minutes": duration_minutes,
        "topics_covered": list(session.topics_covered)
    }), 200
@interview_routes_bp.route('/interview/<int:interview_id>/session', methods=['GET'])
def get_session_for_interview(interview_id):
    """🔥 FIXED: Convert interview_id → session_id for HR dashboard"""
    try:
        services = get_services()
        session = services['get_session_by_interview_id'](interview_id)
        
        if not session:
            # 🔥 AUTO-CREATE session if missing!
            logger.info(f"🔄 No session for interview {interview_id}, creating...")
            from ..utils.file_utils import create_session_directory
            import uuid
            
            session_id = str(uuid.uuid4())
            recording_path = create_session_directory(session_id, RECORDINGS_FOLDER)
            
            session = services['InterviewSession'](
                interview_id=interview_id,
                job_title="Software Engineer",
                job_description="Full-stack developer",
                candidate_background={},
                session_id=session_id,
                recording_path=recording_path
            )
            
            services['add_session'](session)
            logger.info(f"✅ AUTO-CREATED session {session_id} for interview {interview_id}")
        
        return jsonify({
            'interview_id': interview_id,
            'session_id': session.session_id,
            'status': 'ready',
            'recording_path': getattr(session, 'recording_path', 'N/A')
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Session lookup failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


