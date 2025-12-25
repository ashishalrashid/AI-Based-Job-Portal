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
    "contact_email": fields.String,
    "contact_phone": fields.String,
    "offer_accepted": fields.Boolean,
    "status": fields.String,
    "joining_date": fields.String
}

create_onboarding_parser = reqparse.RequestParser()
create_onboarding_parser.add_argument('application_id', type=int, required=True, help="Application ID is required")
create_onboarding_parser.add_argument('contact_email')
create_onboarding_parser.add_argument('contact_phone')
create_onboarding_parser.add_argument('offer_accepted', type=bool)
create_onboarding_parser.add_argument('status')
create_onboarding_parser.add_argument('joining_date')

class OnboardingApi(Resource):
    @marshal_with(output_fields)
    def get(self, onboarding_id=None):
        if onboarding_id:
            onboarding = Onboarding.query.get(onboarding_id)
            return onboarding
        all_onboardings = Onboarding.query.all()
        return all_onboardings

    @marshal_with(output_fields)
    def post(self):
        args = create_onboarding_parser.parse_args()
        application_id = args['application_id']
        application = Application.query.get(application_id)
        if not application:
            return {"message": "Application not found."}, 404

        joining_date = date.fromisoformat(args['joining_date']) if args.get('joining_date') else None

        onboarding = Onboarding(
            application_id=application_id,
            contact_email=args.get('contact_email'),
            contact_phone=args.get('contact_phone'),
            offer_accepted=args.get('offer_accepted', False),
            status=args.get('status', 'pending'),
            joining_date=joining_date
        )
        db.session.add(onboarding)
        db.session.commit()
        return onboarding, 201

    @marshal_with(output_fields)
    def put(self, onboarding_id):
        onboarding = Onboarding.query.get(onboarding_id)
        args = create_onboarding_parser.parse_args()

        application_id = args['application_id']
        application = Application.query.get(application_id)
        if not application:
            return {"message": "Application not found."}, 404
        onboarding.application_id = application_id

        if args.get('contact_email') is not None:
            onboarding.contact_email = args.get('contact_email')
        if args.get('contact_phone') is not None:
            onboarding.contact_phone = args.get('contact_phone')
        if args.get('offer_accepted') is not None:
            onboarding.offer_accepted = args.get('offer_accepted')
        if args.get('status') is not None:
            onboarding.status = args.get('status')
        if args.get('joining_date'):
            onboarding.joining_date = date.fromisoformat(args['joining_date'])

        db.session.commit()
        return onboarding, 200

    def delete(self, onboarding_id):
        onboarding = Onboarding.query.get(onboarding_id)
        db.session.delete(onboarding)
        db.session.commit()
        return "", 200

