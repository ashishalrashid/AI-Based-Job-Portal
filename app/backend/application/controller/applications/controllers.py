from flask import Blueprint, request, jsonify, current_app
from application.data.models import Application, ApplicantProfile, JobPosting, Company
from application.data.database import db
from datetime import datetime, date
import requests

applications_bp = Blueprint('applications', __name__)

# hr side -> all candidates page
@applications_bp.route('/<int:company_id>/candidates', methods=['GET'])
def get_candidates(company_id):

    role = request.args.get('role')
    search = request.args.get('search')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 12))

    # Base query (with company restriction)
    query = (
        db.session.query(
            Application.id.label("application_id"),
            ApplicantProfile.name.label("full_name"),
            ApplicantProfile.gender,
            JobPosting.job_title,
            Application.resume_score
        )
        .join(ApplicantProfile, ApplicantProfile.applicant_id == Application.applicant_id)
        .join(JobPosting, JobPosting.id == Application.job_id)
        .filter(JobPosting.company_id == company_id)    
    )

    if role and role.lower() != "all roles":
        query = query.filter(JobPosting.job_title.ilike(f"%{role}%"))
  
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(ApplicantProfile.name.ilike(search_pattern))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rows = pagination.items

    result = []
    sn = (page - 1) * per_page + 1

    for row in rows:
        first_name, last_name = split_name(row.full_name)

        result.append({
            "sn": sn,
            "first_name": first_name,
            "last_name": last_name,
            "gender": row.gender,
            "role": row.job_title,
            "ai_match_score": row.resume_score,
            "action_url": f"/candidate/{row.application_id}"
        })
        sn += 1

    return jsonify({
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "candidates": result
    }), 200


def split_name(full_name):
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])

# get candidate count for a company
@applications_bp.route('/<int:company_id>/count', methods=['GET'])
def get_candidate_count(company_id):
    count = (
        db.session.query(Application)
        .join(JobPosting, JobPosting.id == Application.job_id)
        .filter(JobPosting.company_id == company_id)
        .count()
    )
    return {"count": count}, 200

# roles for this company (for the dropdown filter)
@applications_bp.route('/<int:company_id>/roles', methods=['GET'])
def get_roles(company_id):
    roles = (
        db.session.query(JobPosting.job_title)
        .filter(JobPosting.company_id == company_id)
        .distinct()
        .all()
    )
    return jsonify([r[0] for r in roles]), 200

# apply for a job
@applications_bp.route('/apply', methods=['POST'])
def apply_for_job():
    data = request.json

    # NOTE: keep your frontend and backend keys in sync
    applicant_id = data.get("applicant_id")
    job_id = data.get("job_id")
    resume_filename = data.get("resume_filename")  # Just the selected resume name

    if not applicant_id or not job_id or not resume_filename:
        return jsonify({"error": "Missing required fields"}), 400

    # Validate applicant
    applicant = ApplicantProfile.query.get(applicant_id)
    if not applicant:
        return jsonify({"error": "Applicant not found"}), 404

    # Validate job
    job = JobPosting.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Prevent duplicate applications
    existing = Application.query.filter_by(
        applicant_id=applicant_id,
        job_id=job_id
    ).first()
    if existing:
        return jsonify({"error": "Already applied to this job"}), 400

    # Create clean Application object
    application = Application(
        job_id=job_id,
        applicant_id=applicant_id,
        status="submitted",
        applied_date=datetime.utcnow(),
        resume_score=None,
        ai_feedback=None
    )

    db.session.add(application)
    db.session.commit()

    # 🔹 Trigger resume parsing synchronously for this applicant+job
    try:
        # Build local URL to existing /resumeparser/parse-resume endpoint
        base_url = request.host_url.rstrip("/")  # e.g. http://127.0.0.1:8086
        parse_url = f"{base_url}/resumeparser/parse-resume"

        resp = requests.post(
            parse_url,
            data={
                "applicantid": str(applicant_id),
                "jobid": str(job_id),
                # no 'force' -> parser will skip if already processed
            },
            timeout=15,
        )
        current_app.logger.info(
            "Triggered resume parsing on apply: %s %s",
            resp.status_code,
            resp.text[:200],
        )
    except Exception as e:
        # Do NOT fail the application just because AI parsing failed
        current_app.logger.error(
            "Failed to trigger resume parsing on apply: %s",
            e,
            exc_info=True,
        )

    return jsonify({
        "message": "Application submitted successfully",
        "application_id": application.id
    }), 201
    
# get all applications for an applicant
@applications_bp.route("/applicant/<int:applicant_id>", methods=["GET"])
def get_applications_for_applicant(applicant_id):

    search = request.args.get("search", "").strip().lower()
    filter_status = request.args.get("status", "").strip().lower()
    sort_by = request.args.get("sort", "recent").strip().lower()

    # Base query
    query = (
        db.session.query(Application, JobPosting, Company)
        .join(JobPosting, Application.job_id == JobPosting.id)
        .join(Company, JobPosting.company_id == Company.id)
        .filter(Application.applicant_id == applicant_id)
    )

    # search filter
    if search:
        query = query.filter(
            db.or_(
                JobPosting.job_title.ilike(f"%{search}%"),
                Company.company_name.ilike(f"%{search}%")
            )
        )

    # status filter
    if filter_status and filter_status != "all":
        query = query.filter(Application.status == filter_status)

    # sorting
    if sort_by == "company":
        query = query.order_by(Company.company_name.asc())

    elif sort_by == "status":
        query = query.order_by(Application.status.asc())

    else:  # default: most recent
        query = query.order_by(Application.applied_date.desc())

    rows = query.all()

    # Build list response
    result = []
    for app, job, company in rows:
        result.append({
            "application_id": app.id,
            "job_title": job.job_title,
            "jobId": app.job_id,
            "company_name": company.company_name,
            "location": job.location,
            "applied_on": str(app.applied_date),
            "work_mode": job.employment_type,
            "status": app.status
        })

    # summary counts
    total = (
        Application.query.filter_by(applicant_id=applicant_id).count()
    )
    shortlisted = (
        Application.query.filter_by(applicant_id=applicant_id, status="shortlisted").count()
    )
    rejected = (
        Application.query.filter_by(applicant_id=applicant_id, status="rejected").count()
    )

    return jsonify({
        "summary": {
            "total": total,
            "shortlisted": shortlisted,
            "rejected": rejected
        },
        "applications": result
    }), 200



