from flask import Blueprint, request, jsonify
from application.data.models import (
    Application, Interview, ApplicantProfile,
    PreviousExperience, PreviousEducation,
    Project, Certification
)
from application.data.database import db
from flask import send_file
import os

from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()

applicant_bp = Blueprint('applicant', __name__)


@applicant_bp.route('/profile/<int:application_id>', methods=['GET'])
def get_candidate_profile(application_id):
    app = Application.query.get_or_404(application_id)
    applicant = app.applicant
    interview = Interview.query.filter_by(application_id=application_id).first()

    return {
        "name": applicant.name,
        "email": applicant.user.email if applicant.user else None,
        "phone": applicant.user.phone if applicant.user else None,
        "linkedin": applicant.linkedin_url,
        "github": applicant.github_url,
        "portfolio": applicant.portfolio_url,

        "resume": {
            "filename": applicant.resume_filename,
            "path": applicant.resume_file_path,
            "uploaded_at": str(applicant.resume_uploaded_at)
        },

        "cover_letter": {
            "filename": applicant.cover_letter_filename,
            "path": applicant.cover_letter_file_path,
            "uploaded_at": str(applicant.cover_letter_uploaded_at)
        },

        "application_status": app.status,
        "interview_feedback": interview.feedback if interview else None,

        "experiences": [
            {
                "position": e.position,
                "company": e.company,
                "start": str(e.start_date),
                "end": str(e.end_date),
                "description": e.description
            } for e in applicant.experiences
        ],

        "educations": [
            {
                "university": ed.university,
                "degree": ed.degree,
                "field": ed.field,
                "grade": ed.grade,
                "grade_out_of": ed.grade_out_of,
                "start": str(ed.start_date),
                "end": str(ed.end_date)
            } for ed in applicant.educations
        ],

        "projects": [
            {
                "title": p.title,
                "description": p.description,
                "technologies": p.technologies,
                "project_url": p.project_url
            } for p in applicant.projects
        ],

        "certifications": [
            {
                "certificate_name": c.certificate_name,
                "issuing_org": c.issuing_organization,
                "issue_date": str(c.issue_date),
                "expiry_date": str(c.expiry_date),
                "credential_id": c.credential_id,
                "credential_url": c.credential_url
            } for c in applicant.certifications
        ],

        "skills": applicant.skills
    }, 200


# EXPERIENCE

@applicant_bp.route('/<int:applicant_id>/experiences', methods=['GET'])
def get_experiences(applicant_id):
    exps = PreviousExperience.query.filter_by(applicant_id=applicant_id).all()
    return jsonify([
        {
            "id": e.id,
            "position": e.position,
            "company": e.company,
            "start": str(e.start_date),
            "end": str(e.end_date),
            "description": e.description
        } for e in exps
    ]), 200


@applicant_bp.route('/<int:applicant_id>/experiences', methods=['POST'])
def add_experience(applicant_id):
    data = request.json
    exp = PreviousExperience(
        applicant_id=applicant_id,
        position=data.get("position"),
        company=data.get("company"),
        start_date=parse_date(data.get("start_date")),
        end_date=parse_date(data.get("end_date")),
        description=data.get("description")
    )
    db.session.add(exp)
    db.session.commit()
    return {"message": "Experience added"}, 201


@applicant_bp.route('/<int:applicant_id>/experiences', methods=['DELETE'])
def delete_all_experiences(applicant_id):
    PreviousExperience.query.filter_by(applicant_id=applicant_id).delete()
    db.session.commit()
    return {"message": "All experiences deleted"}, 200


# EDUCATION 

@applicant_bp.route('/<int:applicant_id>/education', methods=['GET'])
def get_education(applicant_id):
    edus = PreviousEducation.query.filter_by(applicant_id=applicant_id).all()
    return jsonify([
        {
            "id": e.id,
            "university": e.university,
            "degree": e.degree,
            "field": e.field,
            "grade": e.grade,
            "grade_out_of": e.grade_out_of,
            "start": str(e.start_date),
            "end": str(e.end_date)
        } for e in edus
    ]), 200


@applicant_bp.route('/<int:applicant_id>/education', methods=['POST'])
def add_education(applicant_id):
    data = request.json
    edu = PreviousEducation(
        applicant_id=applicant_id,
        university=data.get("university"),
        degree=data.get("degree"),
        field=data.get("field"),
        grade=data.get("grade"),
        grade_out_of=data.get("grade_out_of"),
        start_date=parse_date(data.get("start_date")),
        end_date=parse_date(data.get("end_date"))
    )
    db.session.add(edu)
    db.session.commit()
    return {"message": "Education added"}, 201


@applicant_bp.route('/<int:applicant_id>/education', methods=['DELETE'])
def delete_all_education(applicant_id):
    PreviousEducation.query.filter_by(applicant_id=applicant_id).delete()
    db.session.commit()
    return {"message": "All education deleted"}, 200


# PROJECTS 

@applicant_bp.route('/<int:applicant_id>/projects', methods=['GET'])
def get_projects(applicant_id):
    projs = Project.query.filter_by(applicant_id=applicant_id).all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "technologies": p.technologies,
            "project_url": p.project_url
        } for p in projs
    ]), 200


@applicant_bp.route('/<int:applicant_id>/projects', methods=['POST'])
def add_project(applicant_id):
    data = request.json
    proj = Project(
        applicant_id=applicant_id,
        title=data.get("title"),
        description=data.get("description"),
        technologies=data.get("technologies"),
        project_url=data.get("project_url")
    )
    db.session.add(proj)
    db.session.commit()
    return {"message": "Project added"}, 201


# CERTIFICATIONS

@applicant_bp.route('/<int:applicant_id>/certifications', methods=['GET'])
def get_certifications(applicant_id):
    certs = Certification.query.filter_by(applicant_id=applicant_id).all()
    return jsonify([
        {
            "id": c.id,
            "certificate_name": c.certificate_name,
            "issuing_organization": c.issuing_organization,
            "issue_date": str(c.issue_date),
            "expiry_date": str(c.expiry_date),
            "credential_id": c.credential_id,
            "credential_url": c.credential_url
        } for c in certs
    ]), 200


@applicant_bp.route('/<int:applicant_id>/certifications', methods=['POST'])
def add_certification(applicant_id):
    data = request.json
    cert = Certification(
        applicant_id=applicant_id,
        certificate_name=data.get("certificate_name"),
        issuing_organization=data.get("issuing_organization"),
        issue_date=parse_date(data.get("issue_date")),
        expiry_date=parse_date(data.get("expiry_date")),
        credential_id=data.get("credential_id"),
        credential_url=data.get("credential_url")
    )
    db.session.add(cert)
    db.session.commit()
    return {"message": "Certification added"}, 201


@applicant_bp.route('/<int:applicant_id>/certifications', methods=['DELETE'])
def delete_all_certifications(applicant_id):
    Certification.query.filter_by(applicant_id=applicant_id).delete()
    db.session.commit()
    return {"message": "All certifications deleted"}, 200


@applicant_bp.route('/<int:applicant_id>/download_resume', methods=['GET'])
def download_resume(applicant_id):
    app = ApplicantProfile.query.get_or_404(applicant_id)

    if not app.resume_file_path or not os.path.exists(app.resume_file_path):
        return {"message": "Resume file not found"}, 404

    return send_file(
        app.resume_file_path,
        as_attachment=True,
        download_name=app.resume_filename or "resume.pdf"
    )


@applicant_bp.route('/<int:applicant_id>/download_cover_letter', methods=['GET'])
def download_cover_letter(applicant_id):
    app = ApplicantProfile.query.get_or_404(applicant_id)

    if not app.cover_letter_file_path or not os.path.exists(app.cover_letter_file_path):
        return {"message": "Cover letter not found"}, 404

    return send_file(
        app.cover_letter_file_path,
        as_attachment=True,
        download_name=app.cover_letter_filename or "cover_letter.pdf"
    )
