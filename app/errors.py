from flask import jsonify
from sqlalchemy.exc import IntegrityError
from app import db

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({"error": "An unexpected error occurred"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Malformed Request"}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "You're not allowed to access"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "You're Forbidden to access"}), 403

    @app.errorhandler(IntegrityError)
    def db_integrate(error):
        db.session.rollback()
        return jsonify({"error": "Database error — possibly duplicate or invalid data"}), 400
