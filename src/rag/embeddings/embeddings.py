"""Embedding initialization and management."""

from langchain_huggingface import HuggingFaceEmbeddings


def initialize_embeddings() -> HuggingFaceEmbeddings:
    """Initialize HuggingFace embeddings."""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("✓ Embeddings initialized")
    return embeddings
