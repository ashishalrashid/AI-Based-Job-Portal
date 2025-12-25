from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app
import os, uuid

from application.data.database import db
from application.data.models import (
    Company,
    HRProfile,
    Onboarding,
    JobPosting,
    Interview,
    Application,
)

company_bp = Blueprint("company", __name__)

def ensure_dir(type_):
    d = os.path.join(current_app.root_path, 'uploads', type_)
    os.makedirs(d, exist_ok=True)
    return d

def ok(fn):
    return fn and '.' in fn and fn.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}


@company_bp.route("/dashboard/<int:company_id>", methods=["GET"])
def get_company_dashboard(company_id):
    """
    Returns:
      - total employees (HRs)
      - onboarded last month
      - open job openings
      - hiring summary (12-month aggregate)
    """

    total_employees = (
        HRProfile.query.filter_by(company_id=company_id).count()
    )
    
    total_hrs = (
        HRProfile.query.filter_by(company_id=company_id).count()
    )

    now = datetime.utcnow()

    first_of_this_month = datetime(now.year, now.month, 1)
    first_of_last_month = first_of_this_month - timedelta(days=1)
    first_of_last_month = datetime(first_of_last_month.year, first_of_last_month.month, 1)
    last_of_last_month = first_of_this_month - timedelta(seconds=1)

    onboarded_last_month = (
        Onboarding.query.filter(
            Onboarding.offer_accepted == True,
            Onboarding.joining_date >= first_of_last_month,
            Onboarding.joining_date <= last_of_last_month,
        ).count()
    )

    open_jobs = JobPosting.query.filter_by(company_id=company_id, status="open").count()

    openings_data = (
        db.session.query(
            extract("month", JobPosting.created_date).label("month"),
            extract("year", JobPosting.created_date).label("year"),
            func.count(JobPosting.id),
        )
        .filter(JobPosting.company_id == company_id)
        .group_by("year", "month")
        .all()
    )

    onboarded_data = (
        db.session.query(
            extract("month", Onboarding.joining_date).label("month"),
            extract("year", Onboarding.joining_date).label("year"),
            func.count(Onboarding.id),
        )
        .filter(Onboarding.offer_accepted == True)
        .group_by("year", "month")
        .all()
    )

    interviewing_data = (
        db.session.query(
            extract("month", Interview.interview_date).label("month"),
            extract("year", Interview.interview_date).label("year"),
            func.count(Interview.id),
        )
        .join(Interview.application)
        .join(Application.job)
        .filter(JobPosting.company_id == company_id)
        .group_by("year", "month")
        .all()
    )

    def build_monthly_dict(rows):
        result = {}
        for m, y, count in rows:
            key = f"{int(y)}-{int(m):02d}"
            result[key] = count
        return result

    hiring_summary = {
        "openings": build_monthly_dict(openings_data),
        "onboarded": build_monthly_dict(onboarded_data),
        "interviewing": build_monthly_dict(interviewing_data),
    }

    # Get company name
    company = Company.query.get(company_id)
    company_name = company.company_name if company else None

    return jsonify(
        {
            "total_employees": total_employees,
            "total_hrs": total_hrs,
            "onboarded_last_month": onboarded_last_month,
            "open_job_openings": open_jobs,
            "hiring_summary": hiring_summary,
            "company_name": company_name,
        }
    ), 200


@company_bp.route("/<int:company_id>", methods=["GET"])
def get_company(company_id):
    """Get company details by ID"""
    company = Company.query.get_or_404(company_id)
    return jsonify({
        "id": company.id,
        "company_name": company.company_name,
        "company_email": company.company_email,
        "contact_number": company.contact_number,
        "location": company.location,
        "description": company.description,
        "technology": company.technology,
        "company_size": company.company_size,
    }), 200


@company_bp.route("/<int:company_id>", methods=["PUT"])
def update_company(company_id):
    """Update company profile with optional logo upload"""
    company = Company.query.get_or_404(company_id)
    
    # Handle multipart/form-data for file uploads
    if 'multipart/form-data' in (request.content_type or ''):
        if 'company_name' in request.form:
            company.company_name = request.form.get('company_name')
        if 'company_email' in request.form:
            company.company_email = request.form.get('company_email')
        if 'contact_number' in request.form:
            company.contact_number = request.form.get('contact_number')
        if 'location' in request.form:
            company.location = request.form.get('location')
        if 'description' in request.form:
            company.description = request.form.get('description')
        if 'technology' in request.form:
            company.technology = request.form.get('technology')
        if 'company_size' in request.form:
            company.company_size = request.form.get('company_size')
        
        # Handle logo upload
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                orig = secure_filename(logo_file.filename)
                if orig and ok(orig):
                    if not logo_file.mimetype or not logo_file.mimetype.startswith('image/'):
                        return jsonify({'message': 'Logo must be an image file'}), 400
                    # Store logo in company_logos directory
                    d = ensure_dir('company_logos')
                    ext = os.path.splitext(orig)[1]
                    fn = f"{uuid.uuid4().hex}{ext}"
                    p = os.path.join(d, fn)
                    logo_file.save(p)
                    # Note: If Company model has logo fields, set them here
    else:
        # Handle JSON updates
        data = request.get_json() or {}
        if 'company_name' in data:
            company.company_name = data['company_name']
        if 'company_email' in data:
            company.company_email = data['company_email']
        if 'contact_number' in data:
            company.contact_number = data['contact_number']
        if 'location' in data:
            company.location = data['location']
        if 'description' in data:
            company.description = data['description']
        if 'technology' in data:
            company.technology = data['technology']
        if 'company_size' in data:
            company.company_size = data['company_size']
    
    db.session.commit()
    return jsonify({
        "id": company.id,
        "company_name": company.company_name,
        "company_email": company.company_email,
        "contact_number": company.contact_number,
        "location": company.location,
        "description": company.description,
        "technology": company.technology,
        "company_size": company.company_size,
    }), 200
