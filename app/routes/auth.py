from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import db
from app import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    reqFields = ['name', 'email', 'password', 'role', 'company_id']
    for field in reqFields:
        if field not in data or not data[field]:
            return jsonify({"Error": f"Missing Field: {field}"}), 400

    existingUser = User.query.filter_by(email=data['email']).first()
    if existingUser:
        return jsonify({"Error": "Email Already Registered"}), 400

    newUser = User(
        name=data['name'],
        email=data['email'],
        role=data['role'],
        company_id = data['company_id']
    )

    newUser.setPassword(data['password'])

    db.session.add(newUser)
    db.session.commit()


    return jsonify({"message": "User registered successfully", "user_id": newUser.id}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    reqFields = ['password', 'email']
    for field in reqFields:
        if field not in data or not data[field]:
            return jsonify({"Error": f"Missing Field: {field}"}), 400

    existingUser = User.query.filter_by(email=data['email']).first()
    if not existingUser or not existingUser.checkPassword(data['password']):
        return jsonify({"Error": "Invalid Credentials!"}), 401

    token = create_access_token(identity=str(existingUser.id))

    return jsonify({"message": f"User Loggedin successfully, {token}"}), 200



@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "company_id": user.company_id
    }), 200
