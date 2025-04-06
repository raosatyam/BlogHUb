def register_blueprints(app):
    """Register all blueprints for the application.

    Args:
        app (Flask): The Flask application
    """

    # Import blueprints
    from app.api.auth_api import auth_bp
    from app.api.post_api import post_bp
    from app.api.comment_api import comment_bp
    from app.api.category_api import category_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(post_bp, url_prefix='/api/post')
    app.register_blueprint(comment_bp, url_prefix='/api/comment')
    app.register_blueprint(category_bp, url_prefix='/api/category')

    # pass
