"""Health check endpoints."""
from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/")
async def health_check():
    """Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return {
        "status": "healthy",
        "message": "RAG Agent API is running"
    }


@health_router.get("/status")
async def status():
    """Detailed status endpoint.
    
    Returns:
        JSON response with detailed status information
    """
    return {
        "status": "operational",
        "service": "RAG Agent API",
        "version": "1.0.0"
    }
