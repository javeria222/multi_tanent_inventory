from app import db, bcrypt

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True)
    password_hash = db.Column(db.String, nullable = False)
    role = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)

    def setPassword(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def checkPassword(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
