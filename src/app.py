"""Unified FastAPI + Chainlit Application

This is the main entry point for the Psychology RAG Chatbot application.
It combines:
- FastAPI: High-performance RESTful endpoints for RAG queries and document management
- Chainlit UI: Interactive chat interface mounted at /rag

Architecture:
- API Routes: /health, /documents/*
- Chainlit: Mounted at /rag with interactive chat interface
- Vector Store: Chroma with persistent SQLite
- LLM: Google Gemini (gemini-2.5-flash-lite)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chainlit.utils import mount_chainlit
from fastapi_api.routes import health_router, documents_router
from fastapi_api.utils.error_handler import register_error_handlers


def create_app(config=None):
    """Create and configure the unified FastAPI application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        FastAPI application instance with Chainlit mounted
    """
    app = FastAPI(
        title="Psychology RAG Chatbot API",
        description="RAG-powered API for psychology-informed support",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(documents_router)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Mount Chainlit at /rag
    mount_chainlit(app=app, target="cl_app.py", path="/rag")
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    import uvicorn
    
    print("=" * 70)
    print("Psychology RAG Chatbot - Unified FastAPI Application")
    print("=" * 70)
    print("\n✓ FastAPI initialized")
    print("✓ Chainlit interface mounted at /rag")
    print("\nEndpoints available:")
    print("  - API Health: http://localhost:8000/health")
    print("  - API Status: http://localhost:8000/health/status")
    print("  - Chainlit UI: http://localhost:8000/rag")
    print("  - Document API: http://localhost:8000/documents/*")
    print("  - API Docs: http://localhost:8000/docs")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
