import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import logging

load_dotenv()

db = SQLAlchemy()
DB_NAME = 'database.sqlite3'

def create_database(app):
    if not os.path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
            print(f'Database {DB_NAME} created successfully.')
    else:
        print(f'Database {DB_NAME} already exists.')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{DB_NAME}')
    db.init_app(app)

    # Error Handling
    @app.errorhandler(404)
    def page_not_found(error):
        logging.warning(f"404 Error: {error}")
        return jsonify({'error': 'Page not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"500 Error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    # Login Manager Setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return Customer.query.get(int(user_id))
        except ValueError as e:
            logging.error(f"Failed to load user with ID {user_id}: {e}")
            return None

    # Import Blueprints and Models
    try:
        from .views import views
        from .auth import auth
        from .admin import admin
        from .models import Customer, Cart, Product, Order
    except ImportError as e:
        logging.error(f"Module import failed: {e}")
        raise

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')

    # Create Database
    create_database(app)

    return app



