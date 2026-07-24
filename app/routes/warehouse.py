from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db, Warehouse, Users
from app.utils import requires_role

warehouse_bp = Blueprint('warehouse', __name__)

@warehouse_bp.route('/warehouse', methods=['POST'])
@requires_role('admin')
def create_warehouse():
    data = request.get_json() or {}

    if 'name' not in data or not data['name']:
        return jsonify({"Error": "Missing Required Field: name"}), 400

    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found"}), 404

    new_warehouse = Warehouse(
        name = data['name'],
        location = data.get('location'),
        company_id = user.company_id
    )

    db.session.add(new_warehouse)
    db.session.commit()

    return jsonify({
        "Message": "Warehouse Created Successfully",
        "warehouse": {
            "id": new_warehouse.id,
            "name": new_warehouse.name,
            "location": new_warehouse.location,
            "company_id": new_warehouse.company_id
        }
    }), 201


@warehouse_bp.route('/warehouse', methods=['GET'])
@jwt_required()
def get_warehouse():
    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Warehouse.query.filter_by(company_id=user.company_id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = [
        {
            "id": w.id,
            "name": w.name,
            "location": w.location,
            "company_id": w.company_id
        }
        for w in pagination.items
    ]

    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": per_page
    }), 200

