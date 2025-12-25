from flask import Blueprint, jsonify
from application.data.models import *
from application.data.database import db
from sqlalchemy import func

applicant_dashboard_bp = Blueprint("applicant_dashboard", __name__)

@applicant_dashboard_bp.route("/<int:applicant_id>", methods=["GET"])
def get_applicant_dashboard(applicant_id):

    # Get applicant profile
    profile = ApplicantProfile.query.get_or_404(applicant_id)

    # Applicant name
    applicant_name = profile.name

    # ---- Recent Applications ----
    recent_apps = (
        Application.query
        .filter_by(applicant_id=applicant_id)
        .order_by(Application.applied_date.desc())
        .limit(5)
        .all()
    )

    recent_applications = [
        {
            "job_title": app.job.job_title,
            "company": app.job.company.company_name,
            "status": app.status,
            "applied_date": app.applied_date.isoformat(),
            "application_id": app.id
        }
        for app in recent_apps
    ]

    # ---- Applications by Status ----
    status_counts = {
        "Applied": Application.query.filter_by(applicant_id=applicant_id, status="submitted").count(),
        "Shortlisted": Application.query.filter_by(applicant_id=applicant_id, status="shortlisted").count(),
        "Interview": Application.query.filter_by(applicant_id=applicant_id, status="interview").count(),
        "Offer": Application.query.filter_by(applicant_id=applicant_id, status="offered").count(),
        "Rejected": Application.query.filter_by(applicant_id=applicant_id, status="rejected").count(),
    }

    # ---- Profile Completeness ----
    profile_fields = [
        profile.name,
        profile.address,
        profile.gender,
        profile.highest_qualification,
        profile.institution_name,
        profile.graduation_year,
        profile.skills,
        profile.preferred_location,
        profile.years_of_experience,
        profile.current_job_title,
        profile.linkedin_url,
        profile.github_url,
        profile.portfolio_url,
        profile.current_company,
        profile.notice_period,
        profile.resume_filename,
        profile.cover_letter_filename
    ]

    filled_fields = sum(1 for f in profile_fields if f not in (None, "", "null"))
    total_fields = len(profile_fields)

    profile_completion_percentage = int((filled_fields / total_fields) * 100)

    # ---- Upcoming Interviews ----
    upcoming = (
        Interview.query
        .filter(Interview.interviewee_id == applicant_id)
        .filter(Interview.interview_date >= func.current_date())
        .order_by(Interview.interview_date.asc())
        .all()
    )

    upcoming_interviews = [
        {
            "interview_id": i.id,
            "job_title": i.application.job.job_title,
            "company": i.application.job.company.company_name,
            "date": i.interview_date.isoformat(),
            "stage": i.stage,
            "time": i.slot_start_time.strftime("%H:%M") if i.slot_start_time else None,
            "recording_url": i.interview_recording_url
        }
        for i in upcoming
    ]

    return jsonify({
        "applicant_name": applicant_name,
        "recent_applications": recent_applications,
        "application_status_counts": status_counts,
        "profile_completion": profile_completion_percentage,
        "upcoming_interviews": upcoming_interviews
    }), 200
