from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def require_role(*allowed_roles):
    """Decorator to require a role in the JWT 'role' claim."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return jsonify({"message": "unauthorized"}), 401
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return jsonify({"message": "forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
