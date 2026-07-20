from app import db

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String)
    credit_limit = db.Column(db.Float, default = 0.0)
