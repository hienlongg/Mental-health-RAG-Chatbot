"""Routes package for Flask application."""
from src.flask.routes.health import health_bp
from src.flask.routes.rag import rag_bp
from src.flask.routes.documents import documents_bp

__all__ = ['health_bp', 'rag_bp', 'documents_bp']
