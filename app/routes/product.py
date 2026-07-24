from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.utils import requires_role
from app import Product, db, Users

product_bp = Blueprint('product', __name__)

@product_bp.route('/product', methods=['POST'])
@requires_role('admin')
def create_product():
    data = request.get_json() or {}

    req_field = ['name', 'sku']

    for field in req_field:
        if field not in data or not data[field]:
            return jsonify({"Error": "Missing Required Feild!"}), 400

    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found!"}), 404

    new_prod = Product(
        name = data['name'],
        company_id = user.company_id,
        sku = data['sku'],
        price = data.get('price')
    )

    db.session.add(new_prod)
    db.session.commit()

    return jsonify({
        "Message": "Product Added Successfully",
        "Product": {
            "id": new_prod.id,
            "company_id": new_prod.company_id,
            "name": new_prod.name,
            "sku": new_prod.sku,
            "price": new_prod.price,
            "created_at": new_prod.created_at
        }
    }), 201

@product_bp.route('/product', methods=['GET'])
@jwt_required()
def get_product():
    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found!"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Product.query.filter_by(company_id=user.company_id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = [
        {
            "id": p.id,
            "company_id": p.company_id,
            "name": p.name,
            "sku": p.sku,
            "price": p.price,
            "created_at": p.created_at
        }
        for p in pagination.items
    ]

    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": per_page
    }), 200