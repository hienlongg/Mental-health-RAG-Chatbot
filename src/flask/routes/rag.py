"""RAG pipeline endpoints."""
from flask import Blueprint, request, jsonify
from src.rag.pipeline import RAGPipeline

rag_bp = Blueprint('rag', __name__, url_prefix='/rag')


@rag_bp.before_request
def initialize_pipeline():
    """Initialize RAG pipeline if not already done."""
    # This will be called before each request
    pass


@rag_bp.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint for querying the RAG agent.
    
    Request JSON:
        {
            "query": "Your question here",
            "user_id": "optional_user_id"
        }
    
    Returns:
        JSON response with answer and context
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing required field: query'}), 400
        
        query = data.get('query')
        user_id = data.get('user_id', 'anonymous')
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline()
        
        # Get response from RAG pipeline
        result = rag_pipeline.query(query, user_id=user_id)
        
        return jsonify({
            'success': True,
            'query': query,
            'answer': result.get('answer'),
            'sources': result.get('sources', []),
            'user_id': user_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_bp.route('/query', methods=['POST'])
def query():
    """Alternative query endpoint (alias for chat).
    
    Request JSON:
        {
            "question": "Your question here",
            "user_id": "optional_user_id"
        }
    
    Returns:
        JSON response with answer and context
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Missing required field: question'}), 400
        
        question = data.get('question')
        user_id = data.get('user_id', 'anonymous')
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline()
        
        # Get response from RAG pipeline
        result = rag_pipeline.query(question, user_id=user_id)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': result.get('answer'),
            'sources': result.get('sources', []),
            'user_id': user_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
