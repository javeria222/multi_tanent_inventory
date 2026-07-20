from app import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String, nullable = False)
    sku = db.Column(db.String, nullable = False)
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default = db.func.current_timestamp())
