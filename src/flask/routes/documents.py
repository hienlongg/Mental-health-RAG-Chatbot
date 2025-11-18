"""Document management endpoints."""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

# Configuration for file uploads
UPLOAD_FOLDER = './data/documents'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route('/list', methods=['GET'])
def list_documents():
    """List all uploaded documents.
    
    Returns:
        JSON response with list of documents
    """
    try:
        documents = []
        if os.path.exists(UPLOAD_FOLDER):
            documents = os.listdir(UPLOAD_FOLDER)
        
        return jsonify({
            'success': True,
            'count': len(documents),
            'documents': documents
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload a new document.
    
    Form data:
        file: The document file to upload
    
    Returns:
        JSON response with upload status
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'filename': filename
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@documents_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_document(filename):
    """Delete a document.
    
    Args:
        filename: The name of the file to delete
    
    Returns:
        JSON response with deletion status
    """
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Document not found'}), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully',
            'filename': filename
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@documents_bp.route('/<filename>', methods=['GET'])
def get_document(filename):
    """Get information about a specific document.
    
    Args:
        filename: The name of the file
    
    Returns:
        JSON response with document information
    """
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Document not found'}), 404
        
        file_stats = os.stat(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'size': file_stats.st_size,
            'created': file_stats.st_ctime,
            'modified': file_stats.st_mtime
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
