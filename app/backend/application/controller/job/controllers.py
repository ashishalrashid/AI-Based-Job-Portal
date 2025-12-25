import os
from flask import Blueprint, jsonify, request, send_file, redirect
from application.data.models import Company, ApplicantProfile
from application.data.models import JobPosting, Application, Interview, OfferLetter
from datetime import datetime, date
from application.data.database import db

job_bp = Blueprint('job', __name__)

@job_bp.route('/stats/<int:company_id>', methods=['GET'])
def get_job_stats(company_id):

    jobs = JobPosting.query.filter_by(company_id=company_id).all()
    result = []

    for job in jobs:

        # Applications for this job
        applications = Application.query.filter_by(job_id=job.id).all()
        application_ids = [a.id for a in applications]
        applications_count = len(application_ids)

        # Interview counts
        interviewed_count = (
            Interview.query
            .filter(Interview.application_id.in_(application_ids))
            .count()
        )

        rejected_count = (
            Interview.query
            .filter(Interview.application_id.in_(application_ids))
            .filter(Interview.result == 'rejected')
            .count()
        )

        feedback_pending_count = (
            Interview.query
            .filter(Interview.application_id.in_(application_ids))
            .filter(Interview.status == 'feedback_pending')
            .count()
        )

        # Offers
        offered_count = (
            OfferLetter.query
            .filter(OfferLetter.application_id.in_(application_ids))
            .count()
        )

        # Positions left (treat None num_positions as 0)
        positions_available = int(job.num_positions) if job.num_positions is not None else 0
        positions_left = max(positions_available - offered_count, 0)

        # Days since job was posted
        days_ago = (datetime.utcnow() - job.created_date).days

        result.append({
            "job_id": job.id,
            "job_title": job.job_title,
            "num_positions": job.num_positions,
            "positions_left": positions_left,
            "applications_count": applications_count,
            "interviewed_count": interviewed_count,
            "rejected_count": rejected_count,
            "feedback_pending_count": feedback_pending_count,
            "offered_count": offered_count,
            "days_ago_posted": days_ago
        })

    return jsonify(result), 200


@job_bp.route("/opportunities/<int:applicant_id>", methods=["GET"])
def get_job_opportunities(applicant_id):
    """
    Returns:
        - position
        - company
        - location
        - work mode
        - skills matched (X/Y)
        - pagination
        - search
        - filter by role
    """

    applicant = ApplicantProfile.query.get_or_404(applicant_id)
    applicant_skills = []
    if applicant.skills:
        applicant_skills = [s.strip().lower() for s in applicant.skills.split(",")]

    query = JobPosting.query.join(Company)

    role = request.args.get("role")
    if role and role.lower() != "all jobs":
        query = query.filter(JobPosting.job_title.ilike(f"%{role}%"))

    search = request.args.get("search")
    if search:
        search = f"%{search}%"
        query = query.filter(
            db.or_(
                JobPosting.job_title.ilike(search),
                Company.company_name.ilike(search),
                JobPosting.location.ilike(search)
            )
        )

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    jobs = paginated.items

    results = []

    for job in jobs:
        # Normalize job skills
        job_required_skills = []
        if job.required_skills:
            job_required_skills = [
                s.strip().lower() for s in job.required_skills.split(",")
            ]

        # Skill match count
        match_count = len(
            set(applicant_skills).intersection(set(job_required_skills))
        )
        total_required = len(job_required_skills) if job_required_skills else 0

        results.append({
            "job_id": job.id,
            "position": job.job_title,
            "company": job.company.company_name if job.company else None,
            "location": job.location,
            "work_mode": job.employment_type,
            "skills_matched": f"{match_count}/{total_required}",
        })

    return jsonify({
        "jobs": results,
        "total_jobs": paginated.total,
        "page": paginated.page,
        "total_pages": paginated.pages,
        "per_page": per_page
    }), 200
    

@job_bp.route("/detail/<int:job_id>/<int:applicant_id>", methods=["GET"])
def get_job_details(job_id, applicant_id):
    job = JobPosting.query.get_or_404(job_id)
    company = job.company
    applicant = ApplicantProfile.query.get_or_404(applicant_id)

    days_ago = (date.today() - job.created_date.date()).days

    applicant_skills = []
    if applicant.skills:
        applicant_skills = [s.strip().lower() for s in applicant.skills.split(",")]

    job_skills = []
    if job.required_skills:
        job_skills = [s.strip().lower() for s in job.required_skills.split(",")]

    matched = len(set(applicant_skills).intersection(set(job_skills)))
    total = len(job_skills) if job_skills else 0
    percentage_match = (matched / total) * 100 if total > 0 else 0

    responsibilities = [r.text for r in job.responsibilities]
    requirements = [r.text for r in job.requirements]


    application_count = Application.query.filter_by(job_id=job_id).count()

    # Check if applicant has applied for this job and get application status
    application = Application.query.filter_by(job_id=job_id, applicant_id=applicant_id).first()
    has_applied = application is not None
    application_status = None
    
    if application:
        # Determine UI status based on application, interview, and offer status
        latest_interview = application.interviews.order_by(Interview.id.desc()).first()
        
        # Check for offer letter
        if application.offer_letter:
            if application.offer_letter.status == "accepted":
                application_status = "Offer Accepted"
            else:
                application_status = "Offer Sent"
        # Check for interview status
        elif latest_interview:
            if latest_interview.status == "scheduled":
                application_status = "Interview Scheduled"
            elif latest_interview.status == "completed":
                if latest_interview.result == "rejected":
                    application_status = "Rejected"
                else:
                    application_status = "Interview Completed"
            elif latest_interview.status == "feedback_pending":
                application_status = "Feedback Pending"
            else:
                application_status = "Interview Scheduled"
        # Check application status
        elif application.status == "shortlisted":
            application_status = "Shortlisted"
        elif application.status == "rejected":
            application_status = "Rejected"
        elif application.status == "submitted":
            application_status = "Applied"
        else:
            application_status = application.status.title() if application.status else "Applied"

    response = {
        "job_id": job.id,
        "job_title": job.job_title,
        "company": company.company_name if company else None,
        "company_info": {
            "description": company.description,
            "industry": company.technology,
            "company_size": company.company_size,
            "website": company.website
        },
        "location": job.location,
        "experience_range": job.required_experience,
        "work_mode": job.employment_type,
        "basic_salary": str(job.basic_salary),
        "deadline": job.deadline.isoformat() if job.deadline else None,
        "days_ago_posted": days_ago,
        "job_description": job.job_description,
        "jd_file_url": f"/job/download_jd/{job.id}" if job.attachment_url else None,
        "key_responsibilities": responsibilities,
        "requirements": requirements,
        "required_skills": job_skills,
        "skills_match": {
            "matched": matched,
            "total": total,
            "percentage": round(percentage_match, 2)
        },
        "total_applicants": application_count,
        "has_applied": has_applied,
        "application_status": application_status
    }

    return jsonify(response), 200

@job_bp.route('/download_jd/<int:job_id>', methods=['GET'])
def download_jd(job_id):
    job = JobPosting.query.get(job_id)
    if not job or not job.attachment_url:
        return {"error": "JD not found"}, 404

    file_url = job.attachment_url.strip()

    # If it's a Google Drive URL → convert to direct download
    if "drive.google.com" in file_url:
        direct_url = None

        # Case 1: https://drive.google.com/file/d/<ID>/view?usp=sharing
        if "file/d/" in file_url:
            try:
                file_id = file_url.split("file/d/")[1].split("/")[0]
                direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            except:
                pass

        # Case 2: https://drive.google.com/open?id=<ID>
        if "open?id=" in file_url:
            try:
                file_id = file_url.split("open?id=")[1].split("&")[0]
                direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            except:
                pass

        # Case 3: https://drive.google.com/uc?id=<ID>&export=download
        if "uc?id=" in file_url:
            direct_url = file_url  # already direct

        if not direct_url:
            return {"error": "Unable to process Google Drive link"}, 400

        # → Return a redirect so frontend downloads directly
        return redirect(direct_url, code=302)

    # Otherwise → treat as local file path
    file_path = os.path.abspath(file_url)

    if not os.path.exists(file_path):
        return {"error": "File not found on server"}, 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path)
    )



