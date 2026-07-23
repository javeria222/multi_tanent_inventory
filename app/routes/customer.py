from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import Users, Customer, db
from app.utils import requires_role

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer', methods=['POST'])
@requires_role('admin')
def create_customer():
    data = request.get_json() or {}

    if 'name' not in data or not data['name']:
        return jsonify({"Error": "Missing Required Field: name"}), 400

    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found!"}), 404

    new_customer = Customer(
        name = data['name'],
        email = data['email'],
        credit_limit = data['credit_limit'],
        company_id = user.company_id
    )

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({
        "Message": "Customer Added Successfully",
        "Customer": {
            "id": new_customer.id,
            "email": new_customer.email,
            "name": new_customer.name,
            "company_id": new_customer.company_id,
            "credit_limit": new_customer.credit_limit
        }
    }), 201

@customer_bp.route('/customer', methods=['GET'])
@jwt_required()
def get_customer():
    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found"}), 404

    customers = Customer.query.filter_by(company_id=user.company_id).all()

    result = [
        {
            "id": c.id,
            "email": c.email,
            "name": c.name,
            "company_id": c.company_id,
            "credit_limit": c.credit_limit
        }
        for c in customers
    ]

    return jsonify(result), 200

