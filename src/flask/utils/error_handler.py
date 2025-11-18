"""Error handling utilities for Flask application."""
from flask import jsonify


def register_error_handlers(app):
    """Register error handlers for the Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'status_code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'status_code': 400
        }), 400
