from app import db
from .company import Company

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True)
    password = db.Column(db.String)
    role = db.Column(db.String)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)