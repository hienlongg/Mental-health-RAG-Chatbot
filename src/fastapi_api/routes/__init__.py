"""Routes package for FastAPI application."""
from fastapi_api.routes.health import health_router
from fastapi_api.routes.documents import documents_router

__all__ = ['health_router', 'documents_router']
