from app import db

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String, nullable = False)
    location = db.Column(db.String, nullable = False)
    created_at = db.Column(db.DateTime, default = db.func.current_timestamp())
