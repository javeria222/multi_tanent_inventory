from app import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    status = db.Column(db.String(20), default = 'Pending')
    total_price = db.Column(db.Float, default = 0.0)
    created_at = db.Column(db.DateTime, default = db.func.current_timestamp())
