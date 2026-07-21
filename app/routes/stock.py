from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import Users, Stock, Product, Warehouse, db
from app.utils import requires_role

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/stock', methods=['POST'])
@requires_role('admin')
def create_stock():
    data = request.get_json() or {}

    req_fields = ['product_id', 'warehouse_id', 'quantity']
    for field in req_fields:
        if field not in data or not data[field]:
            return jsonify({"Error": f"Missing required field: {field}"}), 400

    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found!"}), 404

    product = Product.query.filter_by(id=data['product_id'], company_id=user.company_id).first()
    if not product:
        return jsonify({"Error": "Product not found in your company"}), 404

    warehouse = Warehouse.query.filter_by(id=data['warehouse_id'], company_id=user.company_id).first()
    if not warehouse:
        return jsonify({"Error": "Warehouse not found in your company"}), 404

    new_stock = Stock(
        product_id=product.id,
        warehouse_id=warehouse.id,
        quantity=data['quantity']
    )

    db.session.add(new_stock)
    db.session.commit()

    return jsonify({
        "Message": "Stock entry created successfully",
        "Stock": {
            "id": new_stock.id,
            "product_id": new_stock.product_id,
            "warehouse_id": new_stock.warehouse_id,
            "quantity": new_stock.quantity
        }
    }), 201


@stock_bp.route('/stock', methods=['GET'])
@jwt_required()
def get_stock():
    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found"}), 404

    stocks = (
        Stock.query
        .join(Product, Stock.product_id == Product.id)
        .filter(Product.company_id == user.company_id)
        .all()
    )

    result = [
        {
            "id": s.id,
            "product_id": s.product_id,
            "warehouse_id": s.warehouse_id,
            "quantity": s.quantity
        }
        for s in stocks
    ]
    return jsonify(result), 200