"""Main Flask application entry point."""
from flask import Flask
# from routes import health_bp, rag_bp, documents_bp
from routes import health_bp, documents_bp
from utils.error_handler import register_error_handlers


def create_app(config=None):
    """Create and configure the Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configure app
    if config:
        app.config.update(config)
    else:
        app.config.from_object('flask.config')
    
    # Register blueprints
    app.register_blueprint(health_bp)
    # app.register_blueprint(rag_bp)
    app.register_blueprint(documents_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
