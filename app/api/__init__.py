def register_blueprints(app):
    """Register all blueprints for the application.

    Args:
        app (Flask): The Flask application
    """

    # Import blueprints
    from app.api.auth import auth_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # pass
