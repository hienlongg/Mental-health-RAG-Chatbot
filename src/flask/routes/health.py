"""Health check endpoints."""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__, url_prefix='/health')


@health_bp.route('/', methods=['GET'])
def health_check():
    """Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'message': 'RAG Agent API is running'
    }), 200


@health_bp.route('/status', methods=['GET'])
def status():
    """Detailed status endpoint.
    
    Returns:
        JSON response with detailed status information
    """
    return jsonify({
        'status': 'operational',
        'service': 'RAG Agent API',
        'version': '1.0.0'
    }), 200
