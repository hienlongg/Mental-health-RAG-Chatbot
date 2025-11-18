"""Routes package for Flask application."""
from routes.health import health_bp
# from routes.rag import rag_bp
from routes.documents import documents_bp

__all__ = ['health_bp', 
        #    'rag_bp',
             'documents_bp']
