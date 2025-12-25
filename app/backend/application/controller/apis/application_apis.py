from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.exceptions import NotFound, BadRequest
from application.data.database import db
from application.data.models import *
from application.utils.validation import *
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError

output_fields = {
    "id": fields.Integer,
    "job_id": fields.Integer,
    "applicant_id": fields.Integer,    
    "status": fields.String,
    "applied_date": fields.String,
    "resume_score": fields.Integer,
    "ai_feedback": fields.String
}

create_application_parser = reqparse.RequestParser()
create_application_parser.add_argument('job_id', type=int, required=True, help="Job ID is required")
create_application_parser.add_argument('applicant_id', type=int, required=True, help="Applicant ID is required")
create_application_parser.add_argument('status')
create_application_parser.add_argument('applied_date')
create_application_parser.add_argument('resume_score')
create_application_parser.add_argument('ai_feedback')

class ApplicationApi(Resource):
    @marshal_with(output_fields)
    def get(self, application_id=None):
        if application_id:
            application = Application.query.get(application_id)
            return application
        all_applications = Application.query.all()
        return all_applications

    @marshal_with(output_fields)
    def post(self):
        args = create_application_parser.parse_args()
        job_id = args['job_id']
        job = JobPosting.query.get(job_id)
        if not job:
            raise NotFound("Job not found.")
        
        applicant_id = args['applicant_id']
        applicant = ApplicantProfile.query.get(applicant_id)
        if not applicant:
            raise NotFound("Applicant not found.")
        
        application = Application(
            job_id=job_id,
            applicant_id=applicant_id,
            status=args.get('status'),
            applied_date=args.get('applied_date'),
            resume_score=args.get('resume_score'),
            ai_feedback=args.get('ai_feedback')
        )
        db.session.add(application)
        db.session.commit()
        return application, 201

    @marshal_with(output_fields)
    def put(self, application_id):
        application = Application.query.get_or_404(application_id)
        args = create_application_parser.parse_args()

        for field in ["job_id", "applicant_id", "status", "applied_date", "resume_score", "ai_feedback"]:
            value = args.get(field)
            if value is not None:
                setattr(application, field, value)

        db.session.commit()
        return application, 200

    def delete(self, application_id):
        application = Application.query.get(application_id)
        db.session.delete(application)
        db.session.commit()
        return "", 200
