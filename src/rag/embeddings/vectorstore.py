"""Vector store and embedding initialization."""
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
from typing import Optional


def initialize_embeddings(model: str = "models/gemini-embedding-001") -> GoogleGenerativeAIEmbeddings:
    """
    Initialize Google Generative AI embeddings.
    
    Args:
        model: Embedding model name
        
    Returns:
        GoogleGenerativeAIEmbeddings instance
    """
    embeddings = GoogleGenerativeAIEmbeddings(model=model)
    print(f"✓ Embeddings initialized: {model}")
    return embeddings


def initialize_vector_store(
    embeddings: GoogleGenerativeAIEmbeddings,
    collection_name: str = "documents",
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
    if persist_directory:
        persist_directory = str(Path(persist_directory).resolve())
    
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    print(f"✓ Vector store initialized: {collection_name}")
    return vector_store
