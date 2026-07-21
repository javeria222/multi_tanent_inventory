from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwtManager = JWTManager(app)

from app.models.company import Company
from app.models.user import Users
from app.models.customer import Customer
from app.models.order import Orders
from app.models.orderItem import OrderItem
from app.models.product import Product
from app.models.stock import Stock
from app.models.warehouse import Warehouse
from app.routes.auth import auth_bp
from app.routes.warehouse import warehouse_bp
from app.routes.product import product_bp
from app.routes.stock import stock_bp

app.register_blueprint(auth_bp)
app.register_blueprint(warehouse_bp)
app.register_blueprint(product_bp)
app.register_blueprint(stock_bp)

