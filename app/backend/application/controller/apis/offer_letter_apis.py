from flask_restful import Resource, fields, marshal_with, reqparse
from application.data.database import db
from application.data.models import *
from application.utils.validation import *
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

output_fields = {
    "id": fields.Integer,
    "application_id": fields.Integer,
    "candidate_id": fields.Integer,
    "company_id": fields.Integer,
    "joining_date": fields.String,
    "ctc": fields.Integer,
    "generated_date": fields.String,
    "status": fields.String
}

create_offer_letter_parser = reqparse.RequestParser()
create_offer_letter_parser.add_argument('application_id', type=int, required=True, help="Job ID is required")
create_offer_letter_parser.add_argument('candidate_id', type=int, required=True, help="Applicant ID is required")
create_offer_letter_parser.add_argument('company_id', type=int, required=True, help="Company ID is required")
create_offer_letter_parser.add_argument('joining_date')
create_offer_letter_parser.add_argument('ctc')
create_offer_letter_parser.add_argument('status')

class OfferLetterApi(Resource):
    @marshal_with(output_fields)
    def get(self, offer_letter_id=None):
        if offer_letter_id:
            offer_letter = OfferLetter.query.get(offer_letter_id)
            return offer_letter
        all_letters = OfferLetter.query.all()
        return all_letters

    @marshal_with(output_fields)
    def post(self):
        args = create_offer_letter_parser.parse_args()

        application_id = args["application_id"]
        candidate_id = args["candidate_id"]
        company_id = args["company_id"]

        application = Application.query.get(application_id)
        candidate = ApplicantProfile.query.get(candidate_id)
        company = Company.query.get(company_id)

        if not application:
            return {"message": "Application not found"}, 404
        if not candidate:
            return {"message": "Candidate not found"}, 404
        if not company:
            return {"message": "Company not found"}, 404

        joining_date_raw = args.get("joining_date")
        joining_date = None
        if joining_date_raw:
            try:
                joining_date = date.fromisoformat(joining_date_raw)
            except:
                return {"message": "Invalid joining_date"}, 400

        offer_letter = OfferLetter(
            application_id=application_id,
            candidate_id=candidate_id,
            company_id=company_id,
            joining_date=joining_date,
            ctc=args.get("ctc"),
            status=args.get("status", "issued")
        )

        db.session.add(offer_letter)
        db.session.commit()
        return offer_letter, 201

    @marshal_with(output_fields)
    def put(self, offer_letter_id):
        offer_letter = OfferLetter.query.get(offer_letter_id)
        args = create_offer_letter_parser.parse_args()
        offer_letter.application_id = args['application_id']
        offer_letter.candidate_id = args['candidate_id']
        offer_letter.company_id = args['company_id']
        offer_letter.joining_date = date.fromisoformat(args.get('joining_date', offer_letter.joining_date))
        offer_letter.ctc = args.get('ctc', offer_letter.ctc)
        offer_letter.status = args.get('status', offer_letter.status)
        
        db.session.commit()
        return offer_letter, 200

    def delete(self, offer_letter_id):
        offer_letter = OfferLetter.query.get(offer_letter_id)
        db.session.delete(offer_letter)
        db.session.commit()
        return "", 200
