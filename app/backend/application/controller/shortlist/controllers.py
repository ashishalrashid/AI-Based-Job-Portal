from flask import Blueprint, request, jsonify
from sqlalchemy import func
from application.data.models import (
    Application, ApplicantProfile, Interview,
    OfferLetter, JobPosting
)
from application.data.database import db
from sqlalchemy import or_, func

shortlist_bp = Blueprint('shortlist', __name__)

# get stats at the top of the 'shortlisted candidates' page
@shortlist_bp.route('/<int:company_id>/stats', methods=['GET'])
def get_shortlisted_stats(company_id):

    total_shortlisted = (
        Application.query
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .filter(Application.status != 'shorlisted')     # shortlisted means moved ahead
        .count()
    )

    pending_interviews = (
        Interview.query
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .filter(Interview.status == 'pending')
        .count()
    )

    total_offers = (
        OfferLetter.query
        .filter(OfferLetter.company_id == company_id)
        .count()
    )

    accepted_offers = (
        OfferLetter.query
        .filter(OfferLetter.company_id == company_id)
        .filter(OfferLetter.status == 'accepted')
        .count()
    )

    acceptance_rate = (
        (accepted_offers / total_offers) * 100 if total_offers > 0 else 0
    )

    return {
        "total_shortlisted": total_shortlisted,
        "pending_interviews": pending_interviews,
        "offers_sent": total_offers,
        "acceptance_rate": round(acceptance_rate, 2)
    }, 200


# get shortlisted candidates and filter by status, role, search by name
@shortlist_bp.route("/<int:company_id>/candidates", methods=["GET"])
def get_shortlisted_candidates(company_id):

    status_filter = request.args.get("status")
    role_filter = request.args.get("role")
    search = request.args.get("search")

    query = (
        db.session.query(Application)
        .join(Application.applicant)       # ApplicantProfile
        .join(Application.job)            # JobPosting
        .filter(JobPosting.company_id == company_id)
    )

    if status_filter and status_filter.lower() != "all status":

        status_filter = status_filter.lower()

        # Interview-related statuses
        interview_status_map = {
            "pending interview": "scheduled",
            "interview done": "completed",
            "completed": "completed",
            "feedback pending": "feedback_pending"
        }

        # Application-level statuses
        application_status_map = {
            "rejected": "rejected",
        }

        # OfferLetter status (offer accepted or sent)
        offer_status_map = {
            "offer accepted": "accepted"
        }

        # --- INTERVIEW STATUS FILTER ---
        if status_filter in interview_status_map:
            mapped = interview_status_map[status_filter]
            query = query.join(Application.interviews).filter(Interview.status == mapped)

        # --- APPLICATION STATUS FILTER ---
        elif status_filter in application_status_map:
            mapped = application_status_map[status_filter]
            query = query.filter(Application.status == mapped)

        # --- OFFER STATUS FILTER ---
        elif status_filter in offer_status_map:
            mapped = offer_status_map[status_filter]
            query = query.join(Application.offer_letter).filter(OfferLetter.status == mapped)

        # Offer Sent → OfferLetter exists regardless of status
        elif status_filter == "offer sent":
            query = query.join(Application.offer_letter)

    if role_filter and role_filter.lower() != "all roles":
        query = query.join(Application.job).filter(JobPosting.job_title == role_filter)

    if search:
        like = f"%{search}%"
        query = query.join(Application.applicant).filter(
            or_(
                ApplicantProfile.name.ilike(like),
                func.cast(ApplicantProfile.applicant_id, db.String).ilike(like),
            )
        )

    applications = query.all()

    result = []

    for app in applications:
        applicant = app.applicant
        job = app.job

        latest_interview = app.interviews.order_by(Interview.id.desc()).first()

        # UI status mapping
        ui_status = None

        if latest_interview:
            if latest_interview.status == "scheduled":
                ui_status = "pending interview"
            elif latest_interview.status == "completed":
                ui_status = "interview done"
            elif latest_interview.status == "feedback_pending":
                ui_status = "feedback pending"

        # Application-level fallback
        if app.status == "rejected":
            ui_status = "rejected"

        # Offer-related
        if app.offer_letter:
            if app.offer_letter.status == "accepted":
                ui_status = "accepted"
            else:
                ui_status = "offer sent"

        # Include interview result for offer letter eligibility check
        interview_result = None
        if latest_interview:
            interview_result = latest_interview.result

        result.append({
            "application_id": app.id,
            "applicant_id": applicant.applicant_id,
            "first_name": applicant.name.split(" ")[0] if applicant.name else "",
            "last_name": applicant.name.split(" ")[1] if applicant.name and " " in applicant.name else "",
            "gender": applicant.gender,
            "role": job.job_title,
            "ai_match_score": app.resume_score,
            "status": ui_status,
            "interview_result": interview_result  # Add interview result for offer eligibility
        })

    return jsonify(result), 200

@shortlist_bp.route('/reject/<int:application_id>', methods=['PUT'])
def reject_candidate(application_id):
    app = Application.query.get_or_404(application_id)
    app.status = "rejected"
    db.session.commit()
    return {"message": "Candidate rejected successfully"}, 200

