from flask_restful import Resource, fields, marshal_with, reqparse, marshal
from werkzeug.exceptions import NotFound, BadRequest, Conflict
from application.data.database import db
from application.data.models import *
from application.utils.validation import *
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app, request
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import os, uuid

output_fields = {
    "hr_id": fields.Integer,
    "company_id": fields.Integer,    
    "first_name": fields.String,
    "last_name": fields.String,
    "contact_email": fields.String,
    "contact_phone": fields.String,
    "gender": fields.String,
    "username": fields.String,
    "password": fields.String,
    "staff_id": fields.String
}

create_hr_parser = reqparse.RequestParser()
create_hr_parser.add_argument('company_id', type=int, required=True, help="Company ID is required")
create_hr_parser.add_argument('first_name')
create_hr_parser.add_argument('last_name')
create_hr_parser.add_argument('email')
create_hr_parser.add_argument('phone')
create_hr_parser.add_argument('gender')
create_hr_parser.add_argument('username')
create_hr_parser.add_argument('password')
create_hr_parser.add_argument('staff_id')

update_hr_parser = reqparse.RequestParser()
update_hr_parser.add_argument('first_name')
update_hr_parser.add_argument('last_name')
update_hr_parser.add_argument('email')
update_hr_parser.add_argument('phone')
update_hr_parser.add_argument('gender')
update_hr_parser.add_argument('username')
update_hr_parser.add_argument('password')
update_hr_parser.add_argument('staff_id')
update_hr_parser.add_argument('linkedin_url')
update_hr_parser.add_argument('profile_photo', type=FileStorage, location='files')

def ensure_dir(type_):
    d = os.path.join(current_app.root_path, 'uploads', type_)
    os.makedirs(d, exist_ok=True)
    return d

def _del(p):
    if p: 
        try: os.remove(p)
        except: pass

def ok(fn):
    return fn and '.' in fn and fn.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'webp'}

class HRApi(Resource):
    @marshal_with(output_fields)
    def get(self, hr_id=None):
        if hr_id:
            hr = HRProfile.query.get(hr_id)
            return hr
        all_hrs = HRProfile.query.all()
        return all_hrs

    @marshal_with(output_fields)
    def post(self):
        args = create_hr_parser.parse_args()
        company_id = args['company_id']
        company = Company.query.get(company_id)
        if not company:
            raise NotFound("Company not found.")
        
        email = args.get('email')
        password = args.get('password')

        if not email:
            raise BadRequest("email is required to create or associate a user.")

        # Try to find existing user by email
        user = User.query.filter_by(email=email).first()

        try:
            if not user:
                name = "{} {}".format(args.get('first_name') or '', args.get('last_name') or '').strip()
                if not name:
                    name = args.get('username') or email

                if not password:
                    raise BadRequest("password is required when creating a new user.")

                hashed = generate_password_hash(password)
                user = User(name=name, email=email, phone=args.get('phone'), password_hashed=hashed)
                try:
                    user.role = 'hr'
                except Exception:
                    pass
                db.session.add(user)
                db.session.flush()
            else:
                # existing user: ensure they don't already have an HR profile
                existing_hr = HRProfile.query.get(user.id)
                if existing_hr:
                    raise Conflict("User already has an HR profile.")

            hr = HRProfile(hr_id=user.id, company_id=company_id, first_name=args.get('first_name'), last_name=args.get('last_name'), contact_email=email, contact_phone=args.get('phone'), gender=args.get('gender'), username=args.get('username'), password=password, staff_id=args.get('staff_id'))
            db.session.add(hr)
            db.session.commit()
            return hr, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Database error: {}".format(str(e))}, 500

    def put(self, hr_id):
        hr = HRProfile.query.get_or_404(hr_id)
        
        # Check if multipart/form-data for file uploads
        if 'multipart/form-data' in (request.content_type or ''):
            args = update_hr_parser.parse_args()
        else:
            args = update_hr_parser.parse_args()
        
        # Update text fields
        if args.get('first_name') is not None:
            hr.first_name = args['first_name']
        if args.get('last_name') is not None:
            hr.last_name = args['last_name']
        if args.get('email') is not None:
            hr.contact_email = args['email']
        if args.get('phone') is not None:
            hr.contact_phone = args['phone']
        if args.get('gender') is not None:
            hr.gender = args['gender']
        if args.get('username') is not None:
            hr.username = args['username']
        if args.get('password') is not None:
            hr.password = args['password']
        if args.get('staff_id') is not None:
            hr.staff_id = args['staff_id']
        
        # Handle profile photo upload
        photo = args.get('profile_photo')
        if photo:
            orig = secure_filename(photo.filename or '')
            if not orig or not ok(orig): 
                return {'message':'Invalid profile photo'},400
            # Check if it's an image
            if not photo.mimetype or not photo.mimetype.startswith('image/'):
                return {'message':'Profile photo must be an image file'},400
            # Store photo in profile_photos directory
            d = ensure_dir('profile_photos')
            ext = os.path.splitext(orig)[1]
            fn = f"{uuid.uuid4().hex}{ext}"
            p = os.path.join(d,fn)
            photo.save(p)
            # Note: If HRProfile model has photo fields, set them here
            # For now, photo is saved to filesystem but not linked to model
        
        db.session.commit()
        return marshal(hr, output_fields),200

    @marshal_with(output_fields)
    def delete(self, hr_id):
        hr = HRProfile.query.get(hr_id)
        db.session.delete(hr)
        db.session.commit()
        return "", 200
