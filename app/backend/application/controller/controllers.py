from flask import jsonify, make_response, request
from flask import Blueprint
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint to verify backend is running"""
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200

    # Handle GET request
    try:
        response_data = {
            'status': 'healthy',
            'message': 'Backend is running properly',
            'timestamp': datetime.now().isoformat()
        }
        response = make_response(jsonify(response_data), 200)
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response
    except Exception as e:
        print(f"Health check error: {e}")
        error_response = make_response(jsonify({
            'status': 'error',
            'message': 'Backend is running but health check failed',
            'timestamp': datetime.now().isoformat()
        }), 500)
        
        # Add CORS headers to error response
        error_response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        error_response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        error_response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return error_response

@main_bp.route('/roles', methods=["GET"])
def get_roles_users():
    try:
        from application.data.models import User, Role, roles_users
        from application.data.database import db
        num_admins = count_users_by_role('Admin')
        num_sponsors = count_users_by_role('Sponsor')
        num_influencers = count_users_by_role('Influencer')
        
        response = make_response(jsonify({"Admins": num_admins, "Sponsors": num_sponsors, "Influencers": num_influencers}), 200)
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response
    except Exception as e:
        print(f"Roles endpoint error: {e}")
        error_response = make_response(jsonify({"error": "Unable to fetch roles"}), 500)
        
        # Add CORS headers to error response
        error_response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        error_response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        error_response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return error_response

def count_users_by_role(role_name):
    try:
        from application.data.models import User, Role, roles_users
        from application.data.database import db
        from sqlalchemy import func
        return db.session.query(func.count(User.id)).join(roles_users).join(Role).filter(Role.name == role_name).scalar()
    except Exception as e:
        print(f"Count users by role error: {e}")
        return 0
