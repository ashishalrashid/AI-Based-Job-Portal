from application.data.models import Onboarding, Application, JobPosting, ApplicantProfile
from flask import Blueprint, jsonify

onboarding_bp = Blueprint('onboarding', __name__)

@onboarding_bp.route('/pending_count/<int:company_id>', methods=['GET'])
def get_onboarding_pending_count(company_id):
    pending_onboardings = (
        Onboarding.query
        .join(Onboarding.application)
        .join(Application.job)
        .filter(Onboarding.status == 'pending')
        .filter(JobPosting.company_id == company_id)
        .count()
    )
    
    return {'pending_onboarding_count': pending_onboardings}, 200

@onboarding_bp.route('/<int:company_id>', methods=['GET'])
def get_onboardings(company_id):
    """
    Get all onboardings for a company
    Returns list of onboarding records with candidate and job information
    """
    onboardings = (
        Onboarding.query
        .join(Onboarding.application)
        .join(Application.job)
        .join(Application.applicant)
        .filter(JobPosting.company_id == company_id)
        .all()
    )
    
    result = []
    for ob in onboardings:
        result.append({
            "id": ob.id,
            "onboarding_id": ob.id,
            "application_id": ob.application_id,
            "candidate_id": ob.application.applicant_id,
            "candidate_name": ob.application.applicant.name if ob.application.applicant else "N/A",
            "job_title": ob.application.job.job_title if ob.application.job else "N/A",
            "status": ob.status,
            "offer_accepted": ob.offer_accepted,
            "joining_date": ob.joining_date.isoformat() if ob.joining_date else None,
            "contact_email": ob.contact_email,
            "contact_phone": ob.contact_phone,
            "company_id": company_id
        })
    
    return jsonify(result), 200
