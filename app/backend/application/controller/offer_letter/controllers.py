from application.auth.auth import roles_required
from application.data.models import OfferLetter, Application, Interview, JobPosting, ApplicantProfile
from application.data.database import db
from flask import Blueprint, jsonify, request
from application.utils.pdf_utils import generate_offer_letter_pdf
from application.utils.email_utils import send_offer_email
from datetime import date

offer_bp = Blueprint('offer', __name__)

import os

def ensure_offer_letter_dir():
    folder = os.path.join(os.getcwd(), "offer_letters")
    os.makedirs(folder, exist_ok=True)
    return folder

# hr page -> KPIs -> offer acceptance rate
@offer_bp.route('/acceptance_rate/<int:company_id>', methods=['GET'])
def get_acceptance_rate(company_id):
    total_offers = OfferLetter.query.filter_by(company_id=company_id).count()
    accepted_offers = OfferLetter.query.filter_by(company_id=company_id, status='accepted').count()
    if total_offers == 0:
        return {'acceptance_rate': 0}, 200
    acceptance_rate = (accepted_offers / total_offers) * 100
    return {'acceptance_rate': acceptance_rate}, 200

# get selected candidates according to interview status
@offer_bp.route("/eligible/<int:company_id>", methods=["GET"])
def get_eligible_candidates(company_id):
    """
    Get all candidates whose:
    - interview.status = 'completed'
    - interview.result = 'selected'
    Returns interview details along with candidate info for offer letter table
    """

    # Get interviews with selected results
    selected_interviews = (
        db.session.query(Interview)
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .filter(Interview.status == "completed")
        .filter((Interview.result == "selected") | (Interview.result == "approved"))
        .all()
    )

    result = []
    for interview in selected_interviews:
        app = interview.application
        applicant = app.applicant
        job = app.job
        interviewer = interview.interviewer

        result.append({
            # Candidate Info
            "application_id": app.id,
            "candidate_id": applicant.applicant_id,
            "candidate_name": applicant.name,
            "email": applicant.user.email,
            "job_title": job.job_title,
            "basic_salary": str(job.basic_salary) if job.basic_salary else None,
            "employment_type": job.employment_type,
            "location": job.location,
            "company_name": job.company.company_name if job.company else "Company",

            # Interview Info
            "interview_id": interview.id,
            "interview_stage": interview.stage,
            "interview_date": interview.interview_date.isoformat() if interview.interview_date else None,
            "interview_mode": interview.mode,
            "slot_start_time": interview.slot_start_time.strftime("%H:%M") if interview.slot_start_time else None,
            "slot_end_time": interview.slot_end_time.strftime("%H:%M") if interview.slot_end_time else None,
            "duration_minutes": interview.duration_minutes,
            "interviewer_name": f"{interviewer.first_name} {interviewer.last_name}" if interviewer else "Unknown",
            "interview_result": interview.result,
            "interview_feedback": interview.feedback
        })

    return jsonify(result), 200

@offer_bp.route("/send_offer/<int:application_id>", methods=["POST"])
def send_offer(application_id):
    """
    Send offer letter to a candidate
    Accepts optional JSON body with offer details:
    - salary: Annual CTC
    - position: Job position/title
    - start_date: Joining date
    - department: Department name
    - work_mode: Remote/Hybrid/On-site
    - benefits: Additional benefits text
    - valid_until: Offer validity date
    """
    # Get the application first
    application = Application.query.get(application_id)
    if not application:
        return {"error": "Application not found"}, 404

    # Check if candidate is eligible (interview completed and selected/approved)
    interview = Interview.query.filter_by(
        application_id=application_id,
        status="completed"
    ).filter(
        Interview.result.in_(["selected", "approved"])
    ).first()
    
    if not interview:
        # Check if there's any interview for this application to provide better error message
        any_interview = Interview.query.filter_by(application_id=application_id).first()
        if any_interview:
            return {
                "error": f"Candidate is not eligible for offer letter. Interview status: '{any_interview.status}', result: '{any_interview.result}'. Required: status='completed', result='selected'"
            }, 400
        else:
            return {"error": "Candidate is not eligible for offer letter. No interview found for this application."}, 400
    
    # Get offer data from request body (if provided)
    data = request.get_json() or {}
    job = application.job

    # Use provided salary or fallback to job's basic salary
    # Convert salary to int if it's a string
    salary_value = data.get('salary')
    if salary_value:
        try:
            ctc = int(float(str(salary_value).replace(',', '')))
        except (ValueError, TypeError):
            ctc = None
    else:
        ctc = None
    
    # Fallback to job's basic salary if not provided
    if not ctc:
        ctc = job.basic_salary if job.basic_salary else None
    
    if not ctc:
        return {"error": "Salary is required. Please provide salary in the request or ensure the job has a basic salary."}, 400
    
    joining_date = None
    if data.get('start_date'):
        try:
            from datetime import datetime
            joining_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        except (ValueError, TypeError) as e:
            return {"error": f"Invalid start_date format. Expected YYYY-MM-DD, got: {data.get('start_date')}"}, 400

    # Get or create offer letter
    offer = OfferLetter.query.filter_by(application_id=application_id).first()
    if not offer:
        # Create new offer letter
        offer = OfferLetter(
            application_id=application_id,
            candidate_id=application.applicant_id,
            company_id=job.company_id,
            ctc=ctc,
            joining_date=joining_date,
            status="issued"
        )
        db.session.add(offer)
    else:
        # Update existing offer
        offer.ctc = ctc
        if joining_date:
            offer.joining_date = joining_date

    db.session.commit()

    # Extract offer letter specific fields (not stored in DB)
    offer_details = {
        'department': data.get('department', 'Engineering'),
        'work_mode': data.get('work_mode', 'Remote'),
        'benefits': data.get('benefits', 'Standard benefits package')
    }

    # Generate PDF with offer details
    pdf_path = generate_offer_letter_pdf(offer, offer_details)

    # Candidate email and details
    candidate_email = offer.candidate.user.email
    candidate_name = offer.candidate.name
    company_name = job.company.company_name if job.company else "Company"
    job_title = job.job_title

    # Send email with all required details
    send_offer_email(
        to_email=candidate_email,
        pdf_path=pdf_path,
        candidate_name=candidate_name,
        company_name=company_name,
        job_title=job_title,
        application_id=application_id
    )

    # Update status
    offer.status = "sent"
    application.status = "offered"  # Update application status
    interview.result = "offer letter sent"
    db.session.commit()

    return {"message": "Offer letter sent", "offer_id": offer.id}, 200
