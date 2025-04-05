from flask import Flask
from flask_cors import CORS

from config import config_by_name
from app.extensions import db, jwt, limiter, redis_client
from app.api import register_blueprints
from app.middleware.jwt_auth import jwt_manager
from app.middleware.rate_limiter import limiter_manager

def create_app(config_name='development'):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The configuration to use - development, testing, or production

    Returns:
        Flask: The configured Flask application
    """

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize CORS
    CORS(app)

    # Initialize CORS
    db.init_app(app)
    redis_client.initialize(app)

    # jwt.init_app(app)
    jwt_manager.init_app(app)
    limiter_manager.init_app(app)

    # Initialize Redis (not a Flask extension, so handled differently)
    # print(redis_client.client.get("my_key"))

    # Register API blueprints
    register_blueprints(app)

    # Create database tables if they don't exist (in development)
    if config_name == 'development':
        with app.app_context():
            db.create_all()

    @app.route('/health')
    def health_check():
        """Simple health check endpoint."""
        return {'status': 'ok'}

    @app.route('/', methods = ["GET", "POST"])
    def welcome():
        """Welcome endpoint."""
        return {'message': 'Welcome to Blob Hub!!!'}

    return app