"""Unified Flask + Chainlit Application

This is the main entry point for the Psychology RAG Chatbot application.
It combines:
- Flask API: RESTful endpoints for RAG queries and document management
- Chainlit UI: Interactive chat interface mounted at /rag
"""

from flask import Flask
from chainlit.utils import mount_chainlit
from flask_api.routes import health_bp, documents_bp
from flask_api.utils.error_handler import register_error_handlers


def create_app(config=None):
    """Create and configure the unified Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Flask application instance with Chainlit mounted
    """
    app = Flask(__name__)
    
    # Configure app
    if config:
        app.config.update(config)
    else:
        app.config.from_object('flask_api.config')
    
    # Register blueprints for Flask API
    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Mount Chainlit at /rag
    mount_chainlit(app=app, target="cl_app.py", path="/rag")
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print("=" * 70)
    print("Psychology RAG Chatbot - Unified Application")
    print("=" * 70)
    print("\n✓ Flask API initialized")
    print("✓ Chainlit interface mounted at /rag")
    print("\nEndpoints available:")
    print("  - API Health: http://localhost:5000/health")
    print("  - Chainlit UI: http://localhost:5000/rag")
    print("  - Document API: http://localhost:5000/documents/*")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
