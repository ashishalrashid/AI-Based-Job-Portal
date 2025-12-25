import os, re
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app, request
from flask_restful import Resource, fields, marshal_with, reqparse, marshal
from sqlalchemy.exc import SQLAlchemyError
from application.data.database import db
from application.data.models import JobPosting

update_job_parser = reqparse.RequestParser(trim=True, bundle_errors=True)
for name, t in [
    ('hr_id', int),
    ('company_id', int),
    ('job_title', str),
    ('level', str),
    ('basic_salary', int),
    ('num_positions', int),
    ('required_skills', str),
    ('additional_skills', str),
    ('employment_type', str),
    ('duration_months', str),
    ('job_description_ai', str),
    ('job_description', str),
    ('key_responsibilities', str),
    ('required_experience', str),
    ('required_education', str),
    ('location', str),
    ('notice_period', str),
    ('attachment_type', str),
    ('attachment_url', str),
    ('attachment_filename', str),
    ('attachment_mimetype', str),
    ('attachment_size', int),
]:
    update_job_parser.add_argument(name, type=t, location=['json', 'form'])

UPDATABLE_FIELDS = {
    'hr_id', 'company_id', 'job_title', 'level', 'basic_salary',
    'required_skills', 'additional_skills', 'employment_type', 'duration_months',
    'num_positions','job_description_ai', 'job_description', 'key_responsibilities',
    'required_experience', 'required_education', 'location',
    'notice_period', 'attachment_type', 'attachment_url',
    'attachment_filename', 'attachment_mimetype', 'attachment_size'
}

def _is_mapped_attr(model, name: str) -> bool:
    return hasattr(model.__class__, name)

output_fields = {
    "id": fields.Integer,
    "hr_id": fields.Integer,
    "company_id": fields.Integer,    
    "job_title": fields.String,
    "level": fields.String,
    "basic_salary": fields.Integer,
    "num_positions": fields.Integer,
    "required_skills": fields.String,
    "additional_skills": fields.String,
    "employment_type": fields.String,
    "duration_months": fields.String,
    "job_description_ai": fields.String,
    "job_description": fields.String,
    "key_responsibilities": fields.String,
    "required_experience": fields.String,
    "required_education": fields.String,
    "location": fields.String,
    "notice_period": fields.String,
    # attachment metadata 
    "attachment_type": fields.String,      # 'file' or 'gdrive'
    "attachment_url": fields.String,       # server path or Google Drive link
    "attachment_filename": fields.String,
    "attachment_mimetype": fields.String,
    "attachment_size": fields.Integer,
}

# text fields for form-data uploads
create_job_parser = reqparse.RequestParser(trim=True, bundle_errors=True)
create_job_parser.add_argument('hr_id', type=int, location='form')
create_job_parser.add_argument('company_id', type=int, required=False, location='form')
create_job_parser.add_argument('job_title', location='form')
create_job_parser.add_argument('level', location='form')
create_job_parser.add_argument('num_positions', type=int, location='form')
create_job_parser.add_argument('basic_salary', type=int, location='form')
create_job_parser.add_argument('required_skills', location='form')
create_job_parser.add_argument('additional_skills', location='form')
create_job_parser.add_argument('employment_type', location='form')
create_job_parser.add_argument('duration_months', location='form')
create_job_parser.add_argument('job_description_ai', location='form')
create_job_parser.add_argument('job_description', location='form')
create_job_parser.add_argument('key_responsibilities', location='form')
create_job_parser.add_argument('required_experience', location='form')
create_job_parser.add_argument('required_education', location='form')
create_job_parser.add_argument('location', location='form')
create_job_parser.add_argument('notice_period', location='form')
create_job_parser.add_argument('attachment_type', choices=('file', 'gdrive'), location='form')
create_job_parser.add_argument('attachment_url', location='form')  # only for gdrive

create_job_json_parser = reqparse.RequestParser(trim=True, bundle_errors=True)
create_job_json_parser.add_argument('hr_id', type=int, location='json')
create_job_json_parser.add_argument('company_id', type=int, required=False, location='json')
create_job_json_parser.add_argument('job_title', location='json')
create_job_json_parser.add_argument('level', location='json')
create_job_json_parser.add_argument('num_positions', type=int, location='json')
create_job_json_parser.add_argument('basic_salary', type=int, location='json')
create_job_json_parser.add_argument('required_skills', location='json')
create_job_json_parser.add_argument('additional_skills', location='json')
create_job_json_parser.add_argument('employment_type', location='json')
create_job_json_parser.add_argument('duration_months', location='json')
create_job_json_parser.add_argument('job_description_ai', location='json')
create_job_json_parser.add_argument('job_description', location='json')
create_job_json_parser.add_argument('key_responsibilities', location='json')
create_job_json_parser.add_argument('required_experience', location='json')
create_job_json_parser.add_argument('required_education', location='json')
create_job_json_parser.add_argument('location', location='json')
create_job_json_parser.add_argument('notice_period', location='json')
create_job_json_parser.add_argument('attachment_type', choices=('file', 'gdrive'), location='json')
create_job_json_parser.add_argument('attachment_url', location='json')

# file part of multipart/form-data
file_parser = reqparse.RequestParser(trim=True, bundle_errors=True)
file_parser.add_argument('file', type=FileStorage, location='files')

def ensure_upload_dir():
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

_drive_rx = re.compile(r'https?://(drive\.google\.com|docs\.google\.com)/', re.I)


def is_gdrive_url(url: str) -> bool:
    return bool(url and _drive_rx.search(url))

class JobAPI(Resource):
    @marshal_with(output_fields)
    def get(self, job_id=None):
        if job_id:
            job = JobPosting.query.get(job_id)
            return job
        all_jobs = JobPosting.query.all()
        return all_jobs

    def post(self):
        if request.is_json:
            args = create_job_json_parser.parse_args()
        else:
            args = create_job_parser.parse_args()  

        # Validate fields that are required by the DB schema but optional in parsers
        if args.get('hr_id') is None:
            return {"message": "hr_id is required."}, 400
        if not args.get('job_title'):
            return {"message": "job_title is required."}, 400
        
        if not args.get('company_id'):
            return {"message": "Company ID is required when creating a job."}, 400

        attachment_type = args.get('attachment_type')
        attachment_url = None
        attachment_filename = None
        attachment_mimetype = None
        attachment_size = None
        
        if attachment_type == 'file':
            file_args = file_parser.parse_args()
            file = file_args.get('file')
            if not file:
                return {"message": "File is required when attachment_type is 'file'."}, 400
            
            filename = secure_filename(file.filename or '')
            if not filename:
                return {"message": "Invalid file name."}, 400
            
            upload_dir = ensure_upload_dir()
            saved_path = os.path.join(upload_dir, filename)
            try:
                file.save(saved_path)
            except Exception as e:
                current_app.logger.exception("Failed to save uploaded file")
                return {"message": f"Failed to save file: {str(e)}"}, 500
            
            attachment_url = saved_path
            attachment_filename = filename
            attachment_mimetype = file.mimetype
            attachment_size = os.path.getsize(saved_path)
            
        elif attachment_type == 'gdrive':
            url = (args.get('attachment_url') or '').strip()
            if not url:
                return {"message": "attachment_url is required when attachment_type=gdrive"}, 400
            if not is_gdrive_url(url):
                return {"message": "attachment_url must be a Google Drive link"}, 400

            attachment_url = url
            attachment_filename = None
            attachment_mimetype = None
            attachment_size = None
        try:
            job = JobPosting(
                hr_id=args.get('hr_id'),
                company_id=args['company_id'],
                job_title=args.get('job_title'),
                level=args.get('level'),
                basic_salary=args.get('basic_salary'),
                num_positions=args.get('num_positions'),
                required_skills=args.get('required_skills'),
                additional_skills=args.get('additional_skills'),
                employment_type=args.get('employment_type'),
                duration_months=args.get('duration_months'),
                job_description_ai=args.get('job_description_ai'),
                job_description=args.get('job_description'),
                key_responsibilities=args.get('key_responsibilities'),
                required_experience=args.get('required_experience'),
                required_education=args.get('required_education'),
                location=args.get('location'),
                notice_period=args.get('notice_period'),
                attachment_type=attachment_type,
                attachment_url=attachment_url,
                attachment_filename=attachment_filename,
                attachment_mimetype=attachment_mimetype,
                attachment_size=attachment_size,
            )
            db.session.add(job)
            db.session.commit()
            return marshal(job, output_fields), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": f"Database error: {str(e)}"}, 500

    def put(self, job_id):
        job = JobPosting.query.get_or_404(job_id)
        args = update_job_parser.parse_args()

        updated = False
        for key, value in args.items():
            if value is None:
                continue
            if key in UPDATABLE_FIELDS and _is_mapped_attr(job, key):
                setattr(job, key, value)
                updated = True

        if not updated:
            return {"message": "No valid fields to update or all values were null."}, 400

        db.session.commit()
        db.session.refresh(job)  # ensure we return fresh values
        return marshal(job, output_fields), 200

    def delete(self, job_id):
        job = JobPosting.query.get(job_id)
        db.session.delete(job)
        db.session.commit()
        return "", 200
