"""FastAPI configuration settings."""
import os
from pathlib import Path

# Base configuration
BASE_DIR = Path(__file__).parent.parent.parent
DEBUG = os.getenv('FASTAPI_DEBUG', True)
TESTING = os.getenv('FASTAPI_TESTING', False)

# Server configuration
FASTAPI_HOST = os.getenv('FASTAPI_HOST', '0.0.0.0')
FASTAPI_PORT = int(os.getenv('FASTAPI_PORT', 8000))

# Upload configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'data', 'documents'))
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB default
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}

# RAG Pipeline configuration
RAG_EMBEDDINGS_MODEL = os.getenv('RAG_EMBEDDINGS_MODEL', 'models/gemini-embedding-001')
RAG_CHAT_MODEL = os.getenv('RAG_CHAT_MODEL', 'gemini-2.5-flash-lite')
RAG_VECTOR_STORE_DIR = os.getenv('RAG_VECTOR_STORE_DIR', os.path.join(BASE_DIR, 'chroma_langchain_db'))

# API configuration
API_TITLE = 'RAG Agent API'
API_VERSION = '1.0.0'
JSON_SORT_KEYS = False

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
