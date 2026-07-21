from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import Users

def requires_role(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = Users.query.get(int(user_id))

            if not user:
                return jsonify({"Error": "User Not Found!"}), 404

            if user.role == role:
                return f(*args, **kwargs)

            return jsonify({"error": "Access Denied!"}), 403
        return wrapper
    return decorator

