from flask_restful import Resource, fields, marshal_with, marshal, reqparse
from application.data.database import db
from application.data.models import ApplicantProfile
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app, request
from datetime import datetime
import os, uuid

output_fields = {
    "applicant_id": fields.Integer,
    "name": fields.String,
    "address": fields.String,
    "gender": fields.String,
    "highest_qualification": fields.String,
    "institution_name": fields.String,
    "graduation_year": fields.Integer,
    "skills": fields.String,
    "current_company": fields.String,
    "bio": fields.String,
    "location": fields.String,
    "notice_period": fields.String,
    "preferred_location": fields.String,
    "years_of_experience": fields.Integer,
    "current_job_title": fields.String,
    "resume_filename": fields.String,
    "resume_mimetype": fields.String,
    "resume_size": fields.Integer,
    "resume_file_path": fields.String,
    "resume_uploaded_at": fields.String,
    "cover_letter_filename": fields.String,
    "cover_letter_mimetype": fields.String,
    "cover_letter_size": fields.Integer,
    "cover_letter_file_path": fields.String,
    "cover_letter_uploaded_at": fields.String,
    "linkedin_url": fields.String,
    "github_url": fields.String,
    "portfolio_url": fields.String
}

create_applicant_parser = reqparse.RequestParser(trim=True, bundle_errors=True)
for f in [
    'applicant_id','name','address','gender','highest_qualification','institution_name',
    'graduation_year','skills','preferred_location','years_of_experience','current_job_title',
    'bio','location','current_company','notice_period','linkedin_url','github_url','portfolio_url'
]:
    create_applicant_parser.add_argument(f, location='form')
create_applicant_parser.replace_argument('applicant_id', type=int, required=True, location='form')
create_applicant_parser.add_argument('resume', type=FileStorage, location='files')
create_applicant_parser.add_argument('cover_letter', type=FileStorage, location='files')

update_applicant_parser = reqparse.RequestParser(trim=True, bundle_errors=True)
for f in [
    'name','address','gender','highest_qualification','institution_name','graduation_year',
    'skills','preferred_location','years_of_experience','current_job_title',
    'bio','location','current_company','notice_period','linkedin_url','github_url','portfolio_url'
]:
    update_applicant_parser.add_argument(f, location='form')
update_applicant_parser.add_argument('resume', type=FileStorage, location='files')
update_applicant_parser.add_argument('cover_letter', type=FileStorage, location='files')
update_applicant_parser.add_argument('profile_photo', type=FileStorage, location='files')

def ensure_dir(type_):
    d = os.path.join(current_app.root_path, 'uploads', type_)
    os.makedirs(d, exist_ok=True)
    return d

def _del(p):
    if p: 
        try: os.remove(p)
        except: pass

ALLOWED = {".pdf",".doc",".docx"}

def ok(fn): return os.path.splitext(fn)[1].lower() in ALLOWED

MUTABLE = [
    'name','address','gender','highest_qualification','institution_name',
    'graduation_year','skills','preferred_location','years_of_experience',
    'bio','location','current_company','notice_period','current_job_title','linkedin_url','github_url','portfolio_url'
]

def missing(v): return v is None or (isinstance(v,str) and not v.strip())

class ApplicantAPI(Resource):

    @marshal_with(output_fields)
    def get(self, applicant_id=None):
        if applicant_id:
            return ApplicantProfile.query.get(applicant_id)
        return ApplicantProfile.query.all()

    def post(self):
        if 'multipart/form-data' not in (request.content_type or ''):
            return {'message':'Must be multipart/form-data'},415

        args = create_applicant_parser.parse_args()
        applicant_id = args['applicant_id']
        resume = args.get('resume')
        cover = args.get('cover_letter')

        existing = ApplicantProfile.query.get(applicant_id)

        if existing:
            for f in MUTABLE:
                cur = getattr(existing,f)
                new = args.get(f)
                if missing(cur) and new: setattr(existing,f,new)

            if resume:
                orig = secure_filename(resume.filename or '')
                if not orig or not ok(orig): return {'message':'Invalid resume'},400
                _del(existing.resume_file_path)
                d = ensure_dir('resumes')
                ext = os.path.splitext(orig)[1]
                fn = f"{uuid.uuid4().hex}{ext}"
                p = os.path.join(d,fn)
                resume.save(p)
                existing.resume_filename = orig
                existing.resume_mimetype = resume.mimetype
                existing.resume_size = os.path.getsize(p)
                existing.resume_file_path = p
                existing.resume_uploaded_at = datetime.utcnow()

            if cover:
                orig = secure_filename(cover.filename or '')
                if not orig or not ok(orig): return {'message':'Invalid cover letter'},400
                _del(existing.cover_letter_file_path)
                d = ensure_dir('cover_letters')
                ext = os.path.splitext(orig)[1]
                fn = f"{uuid.uuid4().hex}{ext}"
                p = os.path.join(d,fn)
                cover.save(p)
                existing.cover_letter_filename = orig
                existing.cover_letter_mimetype = cover.mimetype
                existing.cover_letter_size = os.path.getsize(p)
                existing.cover_letter_file_path = p
                existing.cover_letter_uploaded_at = datetime.utcnow()

            db.session.commit()
            return marshal(existing, output_fields),200

        if not args.get('name'): return {'message':'name required'},400
        if not resume: return {'message':'resume required'},400

        orig = secure_filename(resume.filename or '')
        if not orig or not ok(orig): return {'message':'Invalid resume'},400
        d = ensure_dir('resumes')
        ext = os.path.splitext(orig)[1]
        fn = f"{uuid.uuid4().hex}{ext}"
        rp = os.path.join(d,fn)
        resume.save(rp)

        cp = None
        if cover:
            corig = secure_filename(cover.filename or '')
            if not corig or not ok(corig): return {'message':'Invalid cover letter'},400
            d2 = ensure_dir('cover_letters')
            ext2 = os.path.splitext(corig)[1]
            cfn = f"{uuid.uuid4().hex}{ext2}"
            cp = os.path.join(d2,cfn)
            cover.save(cp)

        cand = ApplicantProfile(
            applicant_id=applicant_id,
            name=args.get('name'),
            address=args.get('address'),
            gender=args.get('gender'),
            highest_qualification=args.get('highest_qualification'),
            institution_name=args.get('institution_name'),
            graduation_year=args.get('graduation_year'),
            skills=args.get('skills'),
            bio=args.get('bio'),
            location=args.get('location'),
            current_company=args.get('current_company'),
            notice_period=args.get('notice_period'),
            preferred_location=args.get('preferred_location'),
            years_of_experience=args.get('years_of_experience'),
            current_job_title=args.get('current_job_title'),
            resume_filename=orig,
            resume_mimetype=resume.mimetype,
            resume_size=os.path.getsize(rp),
            resume_file_path=rp,
            resume_uploaded_at=datetime.utcnow(),
            cover_letter_filename=(corig if cover else None),
            cover_letter_mimetype=(cover.mimetype if cover else None),
            cover_letter_size=(os.path.getsize(cp) if cover else None),
            cover_letter_file_path=cp,
            cover_letter_uploaded_at=(datetime.utcnow() if cover else None),
            linkedin_url=args.get('linkedin_url'),
            github_url=args.get('github_url'),
            portfolio_url=args.get('portfolio_url')
        )

        try:
            db.session.add(cand)
            db.session.commit()
            return marshal(cand, output_fields),201
        except SQLAlchemyError as e:
            _del(rp)
            if cp: _del(cp)
            db.session.rollback()
            return {'message':str(getattr(e,'orig',e))},500

    def put(self, applicant_id):
        cand = ApplicantProfile.query.get_or_404(applicant_id)
        if 'multipart/form-data' not in (request.content_type or ''):
            return {'message':'Must be multipart/form-data'},415

        args = update_applicant_parser.parse_args()

        for f in MUTABLE:
            v = args.get(f)
            if v is not None: setattr(cand,f,v)

        resume = args.get('resume')
        cover = args.get('cover_letter')
        photo = args.get('profile_photo')

        if resume:
            orig = secure_filename(resume.filename or '')
            if not orig or not ok(orig): return {'message':'Invalid resume'},400
            _del(cand.resume_file_path)
            d = ensure_dir('resumes')
            ext = os.path.splitext(orig)[1]
            fn = f"{uuid.uuid4().hex}{ext}"
            p = os.path.join(d,fn)
            resume.save(p)
            cand.resume_filename = orig
            cand.resume_mimetype = resume.mimetype
            cand.resume_size = os.path.getsize(p)
            cand.resume_file_path = p
            cand.resume_uploaded_at = datetime.utcnow()

        if cover:
            orig = secure_filename(cover.filename or '')
            if not orig or not ok(orig): return {'message':'Invalid cover letter'},400
            _del(cand.cover_letter_file_path)
            d = ensure_dir('cover_letters')
            ext = os.path.splitext(orig)[1]
            fn = f"{uuid.uuid4().hex}{ext}"
            p = os.path.join(d,fn)
            cover.save(p)
            cand.cover_letter_filename = orig
            cand.cover_letter_mimetype = cover.mimetype
            cand.cover_letter_size = os.path.getsize(p)
            cand.cover_letter_file_path = p
            cand.cover_letter_uploaded_at = datetime.utcnow()

        if photo:
            orig = secure_filename(photo.filename or '')
            if not orig or not ok(orig): return {'message':'Invalid profile photo'},400
            # Check if it's an image
            if not photo.mimetype or not photo.mimetype.startswith('image/'):
                return {'message':'Profile photo must be an image file'},400
            # Store photo in profile_photos directory
            d = ensure_dir('profile_photos')
            ext = os.path.splitext(orig)[1]
            fn = f"{uuid.uuid4().hex}{ext}"
            p = os.path.join(d,fn)
            photo.save(p)
            # Note: If ApplicantProfile model has photo fields, set them here
            # For now, photo is saved to filesystem but not linked to model
            # This can be extended when model fields are added

        db.session.commit()
        return marshal(cand, output_fields),200

    def delete(self, applicant_id):
        cand = ApplicantProfile.query.get_or_404(applicant_id)
        _del(cand.resume_file_path)
        _del(cand.cover_letter_file_path)
        db.session.delete(cand)
        db.session.commit()
        return '',200
