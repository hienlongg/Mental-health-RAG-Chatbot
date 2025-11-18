"""Vector store and embedding initialization."""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
from typing import Optional


def initialize_embeddings(model: str = "sentence-transformers/all-MiniLM-L6-v2") -> HuggingFaceEmbeddings:
    """
    Initialize HuggingFace embeddings.
    
    Args:
        model: Embedding model name
        
    Returns:
        HuggingFaceEmbeddings instance
    """
    embeddings = HuggingFaceEmbeddings(model_name=model)
    print(f"✓ Embeddings initialized: {model}")
    return embeddings


def initialize_vector_store(
    embeddings: HuggingFaceEmbeddings,
    collection_name: str = "psychology_knowledge_base",
    persist_directory: Optional[str] = None
) -> Chroma:
    """
    Initialize Chroma vector store.
    
    Args:
        embeddings: Embeddings instance
        collection_name: Name of the collection
        persist_directory: Directory for persistence
        
    Returns:
        Chroma vector store instance
    """
    if persist_directory is None:
        persist_directory = ".data/embeddings/chroma_langchain_db"
    
    if persist_directory:
        persist_directory = str(Path(persist_directory).resolve())
    
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    print(f"✓ Vector store initialized: {collection_name}")
    return vector_store
