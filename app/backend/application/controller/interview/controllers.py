from flask import Blueprint, jsonify, request
from application.data.models import Interview, ApplicantProfile, Application, JobPosting, Company
from application.data.database import db
from datetime import date, datetime, timedelta
from sqlalchemy import extract

interview_bp = Blueprint('interview', __name__)

# hr dashboard -> KPIs -> get count of pending feedback interviews for a company
@interview_bp.route('/feedback_pending/<int:company_id>', methods=['GET'])
def get_interview_feedback_pending_count(company_id):
    pending_interview_feedbacks = (
        Interview.query
        .join(Interview.application)
        .join(Application.job)
        .filter(Interview.status == "feedback_pending")
        .filter(JobPosting.company_id == company_id)
        .count()
    )
    
    return {'pending_interview_feedback_count': pending_interview_feedbacks}, 200

# hr dashboard -> right side panel -> upcoming meetings (filtered by hr)
@interview_bp.route('/sorted_by_date/<int:hr_id>', methods=['GET'])
def get_interviews_for_hr_sorted(hr_id):
    from application.data.models import Application, JobPosting, ApplicantProfile
    
    interviews = (
        Interview.query
        .join(Application, Interview.application_id == Application.id)
        .join(JobPosting, Application.job_id == JobPosting.id)
        .join(ApplicantProfile, Application.applicant_id == ApplicantProfile.applicant_id)
        .filter(Interview.interviewer_id == hr_id)
        .order_by(Interview.interview_date.desc())
        .all()
    )

    from application.data.models import User
    
    result = []
    for i in interviews:
        # Get candidate name and job title from related objects
        candidate_name = 'Candidate'
        job_title = 'Position'
        
        if i.application:
            # Get job title
            if i.application.job:
                job_title = i.application.job.job_title
            
            # Get candidate name from User
            applicant_user = User.query.get(i.application.applicant_id)
            if applicant_user:
                candidate_name = applicant_user.name
        
        result.append({
            "interview_id": i.id,
            "id": i.id,
            "application_id": i.application_id,
            "interview_date": i.interview_date.isoformat() if i.interview_date else None,
            "interviewee_id": i.interviewee_id,
            "mode": i.mode,
            "stage": i.stage,
            "slot_start_time": i.slot_start_time.isoformat() if i.slot_start_time else None,
            "slot_end_time": i.slot_end_time.isoformat() if i.slot_end_time else None,
            "interviewer_id": i.interviewer_id,
            "status": i.status,
            "result": i.result,
            "candidate_name": candidate_name,
            "applicant_name": candidate_name,  # Alias for compatibility
            "job_title": job_title
        })

    return jsonify({"interviews": result}), 200

# schedule interview
@interview_bp.route('/schedule/<int:application_id>/<int:hr_id>', methods=['POST'])
def schedule_interview(application_id, hr_id):
    data = request.json

    stage = data.get("stage")
    interview_date = data.get("interview_date")       # "2025-06-10"
    interview_time = data.get("interview_time")       # "14:30"
    duration = int(data.get("duration", 60))          # minutes

    app = Application.query.get_or_404(application_id)

    # Parse datetime fields
    try:
        date_obj = datetime.strptime(interview_date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(interview_time, "%H:%M").time()
    except ValueError:
        return {"message": "Invalid date or time format"}, 400

    start_dt = datetime.combine(date_obj, time_obj)
    end_dt = start_dt + timedelta(minutes=duration)

    interview = Interview(
        application_id=application_id,
        interview_date=date_obj,
        interviewee_id=app.applicant_id,
        interviewer_id=hr_id,
        mode="online",
        slot_start_time=start_dt.time(),
        slot_end_time=end_dt.time(),
        duration_minutes=duration,
        stage=stage,
        status="scheduled"
    )

    db.session.add(interview)

    # Update application status
    app.status = "interview_scheduled"

    db.session.commit()

    return {
        "message": "Interview scheduled successfully",
        "interview_id": interview.id
    }, 201
    
@interview_bp.route('/reject/<int:application_id>', methods=['POST'])
def reject_candidate(application_id):
    app = Application.query.get_or_404(application_id)

    app.status = "rejected"

    # Cancel pending interviews if any
    Interview.query.filter_by(application_id=application_id).update({
        "status": "cancelled"
    })

    db.session.commit()

    return {"message": "Candidate rejected"}, 200

# scheduled interviews this month
@interview_bp.route('/stats/scheduled_month/<int:company_id>', methods=['GET'])
def scheduled_this_month(company_id):
    today = date.today()
    interviews = (
        Interview.query
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .filter(Interview.status == 'scheduled')
        .filter(extract('month', Interview.interview_date) == today.month)
        .filter(extract('year', Interview.interview_date) == today.year)
        .count()
    )
    return jsonify({"scheduled_this_month": interviews})

# scheduled this week
@interview_bp.route('/stats/scheduled_week/<int:company_id>', methods=['GET'])
def scheduled_this_week(company_id):
    today = date.today()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    interviews = (
        Interview.query
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .filter(Interview.status == 'scheduled')
        .filter(Interview.interview_date >= start_week)
        .filter(Interview.interview_date <= end_week)
        .count()
    )
    return jsonify({"scheduled_this_week": interviews})

# completed interviews
@interview_bp.route('/stats/completed/<int:company_id>', methods=['GET'])
def completed_interviews(company_id):
    count = (
        Interview.query
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .filter(Interview.status == 'completed')
        .count()
    )
    return jsonify({"completed_interviews": count})

# get count of feedback pending interviews according to company_id
@interview_bp.route('/stats/pending_feedback/<int:company_id>', methods=['GET'])
def pending_feedback(company_id):
    count = (
        Interview.query
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .filter(Interview.status == 'feedback_pending')
        .count()
    )
    return jsonify({"pending_feedback": count})

@interview_bp.route('/cards/<int:company_id>', methods=['GET'])
def get_interview_cards(company_id):

    interviews = (
        Interview.query
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .order_by(Interview.interview_date.desc())
        .all()
    )

    result = []

    for i in interviews:
        interviewee = ApplicantProfile.query.get(i.interviewee_id)

        result.append({
            "id": i.id,
            "name": interviewee.name if interviewee else None,
            "initials": "".join([n[0].upper() for n in interviewee.name.split()]) if interviewee else None,
            "stage": i.stage,
            "date": i.interview_date.isoformat() if i.interview_date else None,
            "time": i.slot_start_time.isoformat() if i.slot_start_time else None,
            "status": i.status,
            "result": i.result,
            "application_id": i.application_id,
        })

    return jsonify(result), 200

# get interview evaluation details
@interview_bp.route('/evaluation/<int:interview_id>', methods=['GET'])
def get_interview_evaluation(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    app = interview.application
    applicant = app.applicant
    job = app.job

    return jsonify({
        "candidate": {
            "name": applicant.name,
            "email": applicant.user.email if applicant.user else None,
            "phone": applicant.user.phone if applicant.user else None,
            "experience": f"{applicant.years_of_experience} years" if applicant.years_of_experience else None,
            "current_company": applicant.current_company,
            "notice_period": applicant.notice_period
        },
        "interview": {
            "interview_id": interview.id,
            "application_id": app.id,
            "job_title": job.job_title if job else None,
            "stage": interview.stage,
            "date": interview.interview_date.isoformat() if interview.interview_date else None,
            "time": interview.slot_start_time.isoformat() if interview.slot_start_time else None,
            "status": interview.status,
            "result": interview.result
        },
        "documents": {
            "resume": {
                "filename": applicant.resume_filename,
                "path": applicant.resume_file_path
            },
            "cover_letter": {
                "filename": applicant.cover_letter_filename,
                "path": applicant.cover_letter_file_path
            }
        },
        "application_status": app.status
    }), 200
    
# submit feedback for an interview (changes status from feedback_pending to allow decision)
@interview_bp.route('/feedback/<int:interview_id>', methods=['POST'])
def submit_interview_feedback(interview_id):
    data = request.get_json() or {}
    
    interview = Interview.query.get_or_404(interview_id)
    
    # If interview is in feedback_pending status, update it to allow decision making
    if interview.status == "feedback_pending":
        # Update status to completed (ready for decision) or keep as scheduled if not completed yet
        # For now, we'll set it to completed so it's ready for decision
        interview.status = "completed"
    
    # Store evaluation data if provided (for future use)
    # Note: You may want to create an InterviewEvaluation model to store this data
    # For now, we'll just update the status
    
    db.session.commit()
    
    return jsonify({
        "message": "Feedback submitted successfully",
        "interview_status": interview.status
    }), 200


# approve, reject, on-hold candidate after interview
@interview_bp.route('/decision/<int:interview_id>', methods=['PUT'])
def set_interview_decision(interview_id):
    data = request.get_json()
    decision = data.get("decision")

    if decision not in ["approved", "rejected", "on_hold"]:
        return jsonify({"message": "Invalid decision"}), 400

    interview = Interview.query.get_or_404(interview_id)
    app = interview.application

    # Update interview result
    interview.result = decision
    interview.status = "completed" if decision == "approved" or decision == "rejected" else interview.status

    # Update application status
    app.status = decision

    db.session.commit()

    return jsonify({
        "message": "Decision updated successfully",
        "interview_result": interview.result,
        "application_status": app.status
    }), 200


# interview summary according to applicant_id
@interview_bp.route("/applicant/<int:applicant_id>/summary", methods=["GET"])
def get_interview_summary(applicant_id):

    today = date.today()

    total_scheduled = Interview.query.filter_by(
        interviewee_id=applicant_id, 
        status="scheduled"
    ).count()

    upcoming = Interview.query.filter(
        Interview.interviewee_id == applicant_id,
        Interview.status == "scheduled",
        Interview.interview_date >= today
    ).count()

    completed = Interview.query.filter_by(
        interviewee_id=applicant_id,
        status="completed"
    ).count()

    return jsonify({
        "total": total_scheduled,
        "upcoming": upcoming,
        "completed": completed
    }), 200
    
# get scheduled interviews for applicant
@interview_bp.route("/applicant/<int:applicant_id>/list", methods=["GET"])
def get_all_applicant_interviews(applicant_id):

    interviews = (
        db.session.query(Interview, Application, JobPosting, Company)
        .join(Application, Interview.application_id == Application.id)
        .join(JobPosting, Application.job_id == JobPosting.id)
        .join(Company, JobPosting.company_id == Company.id)
        .filter(Interview.interviewee_id == applicant_id)
        .filter(Interview.status == 'scheduled')
        .all()
    )

    result = []
    for interview, application, job, company in interviews:
        result.append({
            "id": interview.id,
            "interviewid": interview.id,
            "stage": interview.stage,
            "status": interview.status,
            "interview_date": str(interview.interview_date),
            "start_time": str(interview.slot_start_time),
            "end_time": str(interview.slot_end_time),
            "job_title": job.job_title,
            "company_name": company.company_name,
            "application_id": application.id
        })

    return jsonify(result), 200
@interview_bp.route("/<int:interview_id>/start", methods=["POST"])
def start_interview(interview_id):
    """
    Start an AI video interview session for a given interview.
    For now this creates a dummy session_id that the frontend can use.
    """
    # 1) Make sure the interview exists
    interview = Interview.query.get_or_404(interview_id)

    # 2) Read optional metadata from frontend (not strictly required to work)
    data = request.get_json() or {}
    job_title = data.get("job_title")
    job_description = data.get("job_description")
    candidate_background = data.get("candidate_background")

    # 3) Generate a session id (this is what your socket layer will later use)
    session_id = f"session-{interview_id}-{int(datetime.utcnow().timestamp())}"

    # 4) Optionally persist this on the interview (uncomment if you add a column)
    # interview.session_id = session_id
    # db.session.commit()

    return jsonify({
        "session_id": session_id,
        "interview_id": interview_id,
        "job_title": job_title,
        "job_description": job_description,
        "candidate_background": candidate_background,
    }), 200

# cancel interview
@interview_bp.route("/<int:interview_id>/cancel", methods=["PUT"])
def cancel_interview(interview_id):

    interview = Interview.query.get_or_404(interview_id)
    interview.status = "cancelled"

    db.session.commit()

    return jsonify({"message": "Interview cancelled"}), 200
