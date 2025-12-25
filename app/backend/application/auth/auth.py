from functools import wraps
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from application.data.database import db
from application.data.models import *
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['OPTIONS', 'POST'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight request'}), 200

    auth_data = request.get_json()
    name = auth_data['name']
    password = auth_data['password']
    email = auth_data['email']
    phone = auth_data.get('phone', '')

    # normalize email early
    email_lower = email.strip().lower()

    # Disallow registrations from @hr.com domain
    if email_lower.endswith('@hr.com'):
        return jsonify(message="Registrations from @hr.com are not allowed."), 400

    # Get role from request, or infer from email using regex as fallback
    role = auth_data.get('role', None)
    if not role:
        if re.search(r'@company\.com$', email_lower):
            role = 'admin'
        else:
            role = 'applicant'

    email = email_lower

    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            name=name,
            email=email,
            phone=phone,
            password_hashed=generate_password_hash(password)
        )

        role_from_db = Role.query.filter_by(name=role).first()
        if not role_from_db:
            return jsonify(message="Invalid role provided."), 400

        user.roles.append(role_from_db)
        try:
            user.role = role_from_db.name
        except Exception:
            pass

        db.session.add(user)
        db.session.commit()

        user_identity = {
            'id': user.id,
            'name': user.name,
            'role': role_from_db.name
        }
        access_token = create_access_token(identity=user_identity)
        refresh_token = create_refresh_token(identity=user_identity)

        response = jsonify(message="User registered successfully.")
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        if role == 'applicant':
            applicant = ApplicantProfile(name=name, applicant_id=user.id)
            db.session.add(applicant)
            db.session.commit()

        if role == 'hr':
            # Create a basic company for HR user
            company_name = f"{name}'s Company"
            company = Company(
                company_name=company_name,
                user_id=user.id,
                company_email=email,
                contact_number=phone,
                location='Not specified'
            )
            db.session.add(company)
            db.session.flush()  # Get the company ID

            # Split name into first_name and last_name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0] if name_parts else name
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            hr_profile = HRProfile(
                hr_id=user.id,
                company_id=company.id,
                first_name=first_name,
                last_name=last_name,
                contact_email=email,
                contact_phone=phone
            )
            db.session.add(hr_profile)
            db.session.commit()

        if role == 'admin':
            # Get company details from request if provided
            company_name = auth_data.get('company_name', name)
            company = Company(
                company_name=company_name,
                user_id=user.id,
                company_email=email,
                contact_number=phone
            )
            db.session.add(company)
            db.session.commit()

        return response, 201
    else:
        return jsonify(message="User already exists."), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        auth_data = request.get_json()
        email = auth_data['email']
        password = auth_data['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hashed, password):
            role_name = None
            try:
                role_name = getattr(user, 'primary_role', None)
            except Exception:
                role_name = None

            if not role_name:
                # fallback: try dynamic relationship access
                try:
                    first_role = user.roles.first()
                    role_name = first_role.name if first_role else user.role
                except Exception:
                    role_name = user.role

            user_identity = {
                'id': user.id,
                'name': user.name,
                'role': role_name
            }
            access_token = create_access_token(identity=user_identity, expires_delta=timedelta(hours=1))
            refresh_token = create_refresh_token(identity=user_identity)
            
            # NEW CODE
            if role_name == 'company' or role_name == 'admin':
                company = Company.query.filter_by(user_id=user.id).first()
                company_id = company.id if company else None
                payload = {
                    'role': 'company',
                    'company_id': company_id,
                    'message': "Login successful.",
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                }

            elif role_name == 'hr':
                hr_profile = HRProfile.query.filter_by(hr_id=user.id).first()
                company_id = hr_profile.company_id if hr_profile else None
                payload = {
                    'role': 'hr',
                    'hr_id': user.id,
                    'company_id': company_id,
                    'message': "Login successful.",
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                }

            else:
                applicant_profile = ApplicantProfile.query.filter_by(applicant_id=user.id).first()
                payload = {
                    'role': role_name,
                    'applicant_id': (applicant_profile.applicant_id if applicant_profile else user.id),
                    'message': "Login successful.",
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                }

            response = make_response(jsonify(payload), 200)

            # Add CORS headers to successful login response
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
            print("Access token set:", access_token)
            print("Refresh token set:", refresh_token)
            
            return response
        else:
            # Add CORS headers to error response
            error_response = make_response(jsonify(message="Invalid credentials."), 401)
            error_response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
            error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            error_response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            error_response.headers.add('Access-Control-Allow-Credentials', 'true')
            return error_response
    except Exception as e:
        print(f"Login error: {e}")
        # Add CORS headers to exception error response
        error_response = make_response(jsonify(message="Login failed due to server error."), 500)
        error_response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        error_response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        error_response.headers.add('Access-Control-Allow-Credentials', 'true')
        return error_response

@auth_bp.route('/logout', methods=['OPTIONS', 'POST'])
@jwt_required()
def logout():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight request'}), 200

    response = jsonify(message="Logout successful.")
    unset_jwt_cookies(response)
    return response, 200

def roles_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role', '')
            if user_role not in allowed_roles:
                return jsonify({'message': 'Access denied!'}), 403
            return f(*args, **kwargs)

        return wrapper

    return decorator

@auth_bp.route('/admin', methods=['GET'])
@roles_required(['admin'])
def admin():
    return jsonify({'message': 'Welcome, Admin!'})
