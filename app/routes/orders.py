from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import Users, Orders, db, Customer, OrderItem, Product, Stock
from app.utils import requires_role

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['POST'])
@jwt_required()
def add_orders():
    data = request.get_json() or {}

    req_fields = ['customer_id', 'items']
    for field in req_fields:
        if field not in data or not data[field]:
            return jsonify({"Error": f"Missing required field: {field}"}), 400

    if not isinstance(data['items'], list) or len(data['items']) == 0:
        return jsonify({"Error": "Items must be a non-empty list"}), 400

    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found"}), 404

    # Verify the customer belongs to this user's company
    customer = Customer.query.filter_by(id=data['customer_id'], company_id=user.company_id).first()
    if not customer:
        return jsonify({"Error": "Customer not found in your company"}), 404

    new_order = Orders(
        company_id=user.company_id,
        customer_id=customer.id
    )

    db.session.add(new_order) #Order Creation

    total_price = 0
    order_items_to_add = []

    try:
        for item in data['items']:
            if 'product_id' not in item or 'quantity' not in item:
                raise ValueError("Each item needs product_id and quantity")

            quantity = item['quantity']
            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("Quantity must be a positive number")

            # Verify product belongs to this company
            product = Product.query.filter_by(
                id=item['product_id'], company_id=user.company_id
            ).first()
            if not product:
                raise ValueError(f"Product {item['product_id']} not found in your company")

            stock_item = (
                Stock.query
                .filter_by(product_id=product.id)
                .with_for_update()
                .first()
            )

            if not stock_item or stock_item.quantity < quantity:
                raise ValueError(f"Not enough stock for product: {product.name}")

            stock_item.quantity -= quantity

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price
            )
            order_items_to_add.append(order_item)

            total_price += quantity * product.price

    except ValueError as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 400

    new_order.total_price = total_price
    for oi in order_items_to_add:
        db.session.add(oi)

    db.session.commit()

    return jsonify({
        "Message": "Order created successfully",
        "Order": {
            "id": new_order.id,
            "customer_id": new_order.customer_id,
            "status": new_order.status,
            "total_price": new_order.total_price,
            "items": [
                {
                    "product_id": oi.product_id,
                    "quantity": oi.quantity,
                    "unit_price": oi.unit_price
                }
                for oi in order_items_to_add
            ]
        }
    }), 201


@orders_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Orders.query.filter_by(company_id=user.company_id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = [
        {
            "id": w.id,
            "status": w.status,
            "total_price": w.total_price,
            "company_id": w.company_id,
            "customer_id": w.customer_id,
            "created_at": w.created_at
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


@orders_bp.route('/orders/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(order_id):
    data = request.get_json() or {}

    if 'new_status' not in data or not data['new_status']:
        return jsonify({"Error": "Missing required field: new_status"}), 400

    new_status = data['new_status']

    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user:
        return jsonify({"Error": "User Not Found"}), 404

    order = Orders.query.filter_by(id=order_id, company_id=user.company_id).first()
    if not order:
        return jsonify({"Error": "Order not found"}), 404

    allowed_transition = {
        "Pending": ["Confirmed", "Cancelled"],
        "Confirmed": ["Shipped", "Cancelled"],
        "Shipped": ["Delivered", "Returned"],
        "Delivered": ["Returned"],
        "Cancelled": [],
        "Returned": [],
    }

    current_status = order.status

    if new_status not in allowed_transition.get(current_status, []):
        return jsonify({
            "Error": f"Cannot move from '{current_status}' to '{new_status}'"
        }), 400

    # If the order is being cancelled or returned, restore stock
    if new_status in ["Cancelled", "Returned"]:
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        for oi in order_items:
            stock_item = (
                Stock.query
                .filter_by(product_id=oi.product_id)
                .with_for_update()
                .first()
            )
            if stock_item:
                stock_item.quantity += oi.quantity

    order.status = new_status
    db.session.commit()

    return jsonify({
        "Message": "Order status updated successfully",
        "Order": {
            "id": order.id,
            "status": order.status,
            "total_price": order.total_price
        }
    }), 200
