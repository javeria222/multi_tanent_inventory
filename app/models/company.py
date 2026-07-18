from app import db

class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    created_at = db.Column(db.DateTime, default = db.func.current_timestamp())