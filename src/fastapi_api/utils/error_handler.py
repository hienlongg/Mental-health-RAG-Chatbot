"""Error handling utilities for FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def register_error_handlers(app: FastAPI):
    """Register error handlers for the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(404)
    async def not_found(request: Request, exc: Exception):
        """Handle 404 Not Found errors."""
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Endpoint not found",
                "status_code": 404
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation error",
                "details": exc.errors(),
                "status_code": 422
            }
        )
    
    @app.exception_handler(500)
    async def internal_error(request: Request, exc: Exception):
        """Handle 500 Internal Server Error."""
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }
        )
