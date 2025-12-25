from flask import Blueprint, jsonify
from application.data.models import *
from application.data.database import db

applicant_profile_bp = Blueprint("applicant_profile", __name__)

@applicant_profile_bp.route("/<int:applicant_id>", methods=["GET"])
def get_full_profile(applicant_id):

    applicant = ApplicantProfile.query.get_or_404(applicant_id)
    user = applicant.user
    
    skills_list = []
    if applicant.skills:
        skills_list = [s.strip() for s in applicant.skills.split(",")]

    resume_data = {
        "filename": applicant.resume_filename,
        "path": applicant.resume_file_path,
        "uploaded_at": applicant.resume_uploaded_at.isoformat() if applicant.resume_uploaded_at else None
    }

    cover_letter_data = {
        "filename": applicant.cover_letter_filename,
        "path": applicant.cover_letter_file_path,
        "uploaded_at": applicant.cover_letter_uploaded_at.isoformat() if applicant.cover_letter_uploaded_at else None
    }

    experiences = [
        {
            "id": e.id,
            "company": e.company,
            "position": e.position,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "description": e.description
        }
        for e in applicant.experiences
    ]

    educations = [
        {
            "id": ed.id,
            "university": ed.university,
            "degree": ed.degree,
            "field": ed.field,
            "grade": ed.grade,
            "grade_out_of": ed.grade_out_of,
            "start_date": ed.start_date.isoformat() if ed.start_date else None,
            "end_date": ed.end_date.isoformat() if ed.end_date else None
        }
        for ed in applicant.educations
    ]

    certifications = [
        {
            "id": c.id,
            "certificate_name": c.certificate_name,
            "issuing_organization": c.issuing_organization,
            "issue_date": c.issue_date.isoformat() if c.issue_date else None,
            "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
            "credential_id": c.credential_id,
            "credential_url": c.credential_url
        }
        for c in applicant.certifications
    ]

    return jsonify({
        "personal_info": {
            "name": applicant.name,
            "email": user.email,
            "phone": user.phone,
            "location": applicant.location or applicant.preferred_location,
            "bio": applicant.bio,
        },
        "skills": skills_list,
        "resume": resume_data,
        "cover_letter": cover_letter_data,
        "work_experience": experiences,
        "education": educations,
        "certifications": certifications
    }), 200
