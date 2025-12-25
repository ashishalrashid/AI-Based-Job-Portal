from flask_restful import Resource, fields, marshal_with, reqparse
from flask import Blueprint, jsonify, request
from application.data.database import db
from application.data.models import *
from application.utils.validation import *
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, time, datetime, timedelta  # ✅ UPDATED: Added datetime, timedelta
import os
import json

# ============= EXISTING CRUD API (UNCHANGED) =============

output_fields = {
    "id": fields.Integer,
    "application_id": fields.Integer,
    "interview_date": fields.String,
    "mode": fields.String,
    "stage": fields.String,
    "duration_minutes": fields.Integer,
    "slot_start_time": fields.String,
    "slot_end_time": fields.String,
    "interviewer_id": fields.Integer,
    "interviewee_id": fields.Integer,
    "interview_recording_url": fields.String,
    "status": fields.String,
    "result": fields.String
}

create_interview_parser = reqparse.RequestParser()
create_interview_parser.add_argument('application_id', type=int, required=True, help="Application ID is required")
create_interview_parser.add_argument('interview_date')
create_interview_parser.add_argument('mode')
create_interview_parser.add_argument('stage')
create_interview_parser.add_argument('duration_minutes', type=int)
create_interview_parser.add_argument('slot_start_time')
create_interview_parser.add_argument('slot_end_time')
create_interview_parser.add_argument('interviewer_id', type=int)
create_interview_parser.add_argument('interviewee_id', type=int)
create_interview_parser.add_argument('interview_recording_url')
create_interview_parser.add_argument('status')
create_interview_parser.add_argument('result')

class InterviewApi(Resource):
    @marshal_with(output_fields)
    def get(self, interview_id=None):
        if interview_id:
            interview = Interview.query.get(interview_id)
            return interview
        all_interviews = Interview.query.all()
        return all_interviews

    @marshal_with(output_fields)
    def post(self):
        args = create_interview_parser.parse_args()
        application_id = args['application_id']
        application = Application.query.get(application_id)
        if not application:
            return {"message": "Application not found."}, 404

        interviewer_id = args.get('interviewer_id')
        if interviewer_id:
            interviewer = HRProfile.query.get(interviewer_id)
            if not interviewer:
                return {"message": "Interviewer not found."}, 404
            
        interviewee_id = args.get('interviewee_id')
        if interviewee_id:
            interviewee = ApplicantProfile.query.get(interviewee_id)
            if not interviewee:
                return {"message": "Interviewee not found."}, 404

        interview_date = date.fromisoformat(args['interview_date']) if args.get('interview_date') else None
        slot_start_time = time.fromisoformat(args['slot_start_time']) if args.get('slot_start_time') else None
        slot_end_time = time.fromisoformat(args['slot_end_time']) if args.get('slot_end_time') else None

        interview = Interview(
            application_id=application_id,
            interview_date=interview_date,
            mode=args.get('mode'),
            stage=args.get('stage'),
            slot_start_time=slot_start_time,
            slot_end_time=slot_end_time,
            duration_minutes=args.get('duration_minutes'),
            interviewer_id=interviewer_id,
            interviewee_id=interviewee_id,
            interview_recording_url=args.get('interview_recording_url'),
            status=args.get('status', 'scheduled'),
            result=args.get('result')
        )
        db.session.add(interview)
        db.session.commit()
        return interview, 201

    @marshal_with(output_fields)
    def put(self, interview_id):
        interview = Interview.query.get(interview_id)
        args = create_interview_parser.parse_args()

        application_id = args['application_id']
        application = Application.query.get(application_id)
        if not application:
            return {"message": "Application not found."}, 404
        interview.application_id = application_id

        interviewer_id = args.get('interviewer_id')
        if interviewer_id:
            interviewer = HRProfile.query.get(interviewer_id)
            if not interviewer:
                return {"message": "Interviewer not found."}, 404
            interview.interviewer_id = interviewer_id
            
        interviewee_id = args.get('interviewee_id')
        if interviewee_id:
            interviewee = ApplicantProfile.query.get(interviewee_id)
            if not interviewee:
                return {"message": "Interviewee not found."}, 404
            interview.interviewee_id = interviewee_id

        if args.get('interview_date'):
            interview.interview_date = date.fromisoformat(args['interview_date'])
        if args.get('mode') is not None:
            interview.mode = args.get('mode')
        if args.get('stage') is not None:
            interview.stage = args.get('stage')
        if args.get('duration_minutes') is not None:
            interview.duration_minutes = args.get('duration_minutes')
        if args.get('interview_recording_url') is not None:
            interview.interview_recording_url = args.get('interview_recording_url')
        if args.get('slot_start_time'):
            interview.slot_start_time = time.fromisoformat(args['slot_start_time'])
        if args.get('slot_end_time'):
            interview.slot_end_time = time.fromisoformat(args['slot_end_time'])
        if args.get('status') is not None:
            interview.status = args.get('status')
        if args.get('result') is not None:
            interview.result = args.get('result')

        db.session.commit()
        return interview, 200

    def delete(self, interview_id):
        interview = Interview.query.get(interview_id)
        db.session.delete(interview)
        db.session.commit()
        return "", 200

# ✅ NEW: DUPLICATE PREVENTION HELPER
def check_existing_interview(application_id):
    """
    Check if an active interview already exists for this application.
    Returns existing interview if found, None otherwise.
    Checks for: scheduled, in_progress, or completed status.
    """
    existing = Interview.query.filter(
        Interview.application_id == application_id,
        Interview.status.in_(['scheduled', 'in_progress', 'completed'])
    ).first()
    return existing

# ✅ NEW: SCHEDULE INTERVIEW PARSER
schedule_interview_parser = reqparse.RequestParser()
schedule_interview_parser.add_argument('interview_date', type=str, required=True, help="Interview date (YYYY-MM-DD)")
schedule_interview_parser.add_argument('interview_time', type=str, required=True, help="Interview time (HH:MM)")
schedule_interview_parser.add_argument('duration', type=int, default=60, help="Duration in minutes")
schedule_interview_parser.add_argument('stage', type=str, default='Technical Round')
schedule_interview_parser.add_argument('mode', type=str, default='online')

# ✅ NEW: SCHEDULE INTERVIEW RESOURCE (CRITICAL)
class ScheduleInterviewResource(Resource):
    """
    ✅ Schedule an interview with duplicate prevention.
    POST /api/interview/schedule/<int:application_id>/<int:hr_id>
    """
    
    def post(self, application_id, hr_id):
        try:
            args = schedule_interview_parser.parse_args()
            
            interview_date_str = args['interview_date']
            interview_time_str = args['interview_time']
            duration = args['duration']
            stage = args.get('stage', 'Technical Round')
            mode = args.get('mode', 'online')
            
            # Validate date/time format
            try:
                interview_date = datetime.strptime(interview_date_str, "%Y-%m-%d").date()
                interview_time_obj = datetime.strptime(interview_time_str, "%H:%M").time()
            except ValueError as e:
                return {
                    "message": "Invalid date or time format. Use YYYY-MM-DD and HH:MM",
                    "error": str(e)
                }, 400
            
            # Check if application exists
            application = Application.query.get(application_id)
            if not application:
                return {
                    "message": "Application not found.",
                    "application_id": application_id
                }, 404
            
            # Check if HR exists
            hr = HRProfile.query.get(hr_id)
            if not hr:
                return {
                    "message": "HR profile not found.",
                    "hr_id": hr_id
                }, 404
            
            # ✅ CRITICAL: Check for existing interview
            existing_interview = check_existing_interview(application_id)
            if existing_interview:
                return {
                    "message": f"An interview is already {existing_interview.status.lower()} for this application.",
                    "conflict": True,
                    "existing_interview": {
                        "id": existing_interview.id,
                        "interview_date": str(existing_interview.interview_date),
                        "interview_time": str(existing_interview.slot_start_time),
                        "status": existing_interview.status,
                        "stage": existing_interview.stage
                    }
                }, 409  # HTTP 409 Conflict
            
            # Validate date/time is in future
            now = datetime.now()
            scheduled_datetime = datetime.combine(interview_date, interview_time_obj)
            if scheduled_datetime < now:
                return {
                    "message": "Interview date and time must be in the future.",
                    "provided": str(scheduled_datetime)
                }, 400
            
            # Validate duration
            if duration < 15 or duration > 480:
                return {
                    "message": "Interview duration must be between 15 and 480 minutes.",
                    "provided": duration
                }, 400
            
            # Calculate end time
            slot_end_time = (
                datetime.combine(interview_date, interview_time_obj) + timedelta(minutes=duration)
            ).time()
            
            # Create interview
            interview = Interview(
                application_id=application_id,
                interview_date=interview_date,
                slot_start_time=interview_time_obj,
                slot_end_time=slot_end_time,
                duration_minutes=duration,
                mode=mode,
                stage=stage,
                interviewer_id=hr_id,
                interviewee_id=application.applicant_id,
                status='scheduled'
            )
            
            # Update application status
            application.status = 'interview_scheduled'
            
            # Save to database
            try:
                db.session.add(interview)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                return {
                    "message": "Database error while scheduling interview.",
                    "error": str(e)
                }, 500
            
            return {
                "message": "Interview scheduled successfully.",
                "success": True,
                "interview": {
                    "id": interview.id,
                    "application_id": interview.application_id,
                    "interview_date": str(interview.interview_date),
                    "interview_time": str(interview.slot_start_time),
                    "duration": interview.duration_minutes,
                    "stage": interview.stage,
                    "mode": interview.mode,
                    "status": interview.status
                }
            }, 201
            
        except Exception as e:
            print(f"Error scheduling interview: {e}")
            return {
                "message": "An unexpected error occurred.",
                "error": str(e)
            }, 500

# ============= UPDATED: INTERVIEW BY APPLICATION =============
class InterviewByApplication(Resource):
    """
    ✅ Fetch all interviews for a specific application.
    GET /api/interview/by-application/<int:application_id>
    """
    def get(self, application_id):
        try:
            interviews = Interview.query.filter_by(application_id=application_id).all()
            
            data = []
            for interview in interviews:
                data.append({
                    "id": interview.id,
                    "application_id": interview.application_id,
                    "status": interview.status,
                    "interview_date": str(interview.interview_date) if interview.interview_date else None,
                    "slot_start_time": str(interview.slot_start_time) if interview.slot_start_time else None,
                    "slot_end_time": str(interview.slot_end_time) if interview.slot_end_time else None,
                    "duration_minutes": interview.duration_minutes,
                    "stage": interview.stage,
                    "mode": interview.mode,
                    "interviewer_id": interview.interviewer_id,
                    "result": interview.result
                })
            
            return jsonify(data), 200
        except Exception as e:
            return {'error': str(e)}, 500

# ============= NEW: HR INTERVIEW ENDPOINTS =============

# Helper function to extract session_id from recording URL
def extract_session_id(recording_url):
    """Extract session_id from /static/recordings/{session_id}/video.mp4"""
    if not recording_url:
        return None
    try:
        parts = recording_url.split('/')
        if len(parts) >= 4 and 'recordings' in parts:
            idx = parts.index('recordings')
            return parts[idx + 1]
    except:
        return None
    return None

# Helper function to load JSON file
def load_json_file(filepath):
    """Safely load JSON file, return empty dict on failure"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return {}

# Helper function to get recordings path
def get_recordings_path():
    """Get absolute path to recordings directory"""
    from flask import current_app
    return os.path.join(current_app.root_path, '..', 'recordings')

class HRInterviewList(Resource):
    """GET /api/hr/interviews/<company_id> - List completed interviews for HR dashboard"""
    
    def get(self, company_id):
        try:
            interviews = db.session.query(
                Interview,
                Application,
                JobPosting,
                ApplicantProfile
            ).join(
                Application, Interview.application_id == Application.id
            ).join(
                JobPosting, Application.job_id == JobPosting.id
            ).join(
                ApplicantProfile, Application.applicant_id == ApplicantProfile.applicant_id
            ).filter(
                JobPosting.company_id == company_id,
                Interview.status == 'completed',
                Interview.interview_recording_url.isnot(None)
            ).order_by(
                Interview.interview_date.desc()
            ).all()
            
            result = []
            recordings_base = get_recordings_path()
            
            for interview, application, job, applicant in interviews:
                session_id = extract_session_id(interview.interview_recording_url)
                
                metadata = {}
                evaluation = {}
                
                if session_id:
                    session_path = os.path.join(recordings_base, session_id)
                    metadata = load_json_file(os.path.join(session_path, 'metadata.json'))
                    evaluation = load_json_file(os.path.join(session_path, 'evaluation.json'))
                
                result.append({
                    'interview_id': interview.id,
                    'session_id': session_id,
                    'candidate_name': applicant.name,
                    'job_title': job.job_title,
                    'interview_date': interview.interview_date.isoformat() if interview.interview_date else None,
                    'stage': interview.stage,
                    'duration_minutes': metadata.get('duration_minutes', 0),
                    'questions_asked': metadata.get('questions_asked', 0),
                    'overall_rating': evaluation.get('overall_rating', 0),
                    'recommendation': evaluation.get('recommendation', 'N/A'),
                    'video_url': interview.interview_recording_url,
                    'application_id': application.id,
                    'application_status': application.status
                })
            
            return jsonify(result)
            
        except Exception as e:
            return {'error': str(e)}, 500

class HRInterviewDetail(Resource):
    """GET /api/hr/interview/<session_id> - Get full interview details with AI evaluation"""
    
    def get(self, session_id):
        try:
            recordings_base = get_recordings_path()
            session_path = os.path.join(recordings_base, session_id)
            
            if not os.path.exists(session_path):
                return {'error': 'Interview recording not found'}, 404
            
            metadata = load_json_file(os.path.join(session_path, 'metadata.json'))
            evaluation = load_json_file(os.path.join(session_path, 'evaluation.json'))
            
            transcript = ''
            transcript_path = os.path.join(session_path, 'transcript.txt')
            try:
                if os.path.exists(transcript_path):
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        transcript = f.read()
            except:
                transcript = 'Transcript not available'
            
            video_file = f'/static/recordings/{session_id}/video.mp4'
            audio_file = f'/static/recordings/{session_id}/audio.m4a'
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'metadata': metadata,
                'evaluation': evaluation,
                'transcript': transcript,
                'video_url': video_file,
                'audio_url': audio_file,
                'files_exist': {
                    'video': os.path.exists(os.path.join(session_path, 'video.mp4')),
                    'audio': os.path.exists(os.path.join(session_path, 'audio.m4a'))
                }
            })
            
        except Exception as e:
            return {'error': str(e)}, 500

# ============= BLUEPRINT FOR NEW ENDPOINTS =============

hr_interview_bp = Blueprint('hr_interviews', __name__)

@hr_interview_bp.route('/api/hr/interviews/<int:company_id>', methods=['GET'])
def get_hr_interviews_list(company_id):
    """Alternative Flask route"""
    resource = HRInterviewList()
    return resource.get(company_id)

@hr_interview_bp.route('/api/hr/interview/<session_id>', methods=['GET'])
def get_hr_interview_detail(session_id):
    """Alternative Flask route"""
    resource = HRInterviewDetail()
    return resource.get(session_id)

