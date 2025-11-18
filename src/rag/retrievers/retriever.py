"""Retriever module for similarity search."""

import logging
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def retrieve_context(vector_store: Chroma, query: str, k: int = 2) -> str:
    """
    Search the vector store for relevant documents.
    
    Args:
        vector_store: The Chroma vector store instance
        query: The search query
        k: Number of documents to retrieve
        
    Returns:
        Formatted string with retrieved documents
    """
    logger.info(f"🔍 Retrieving context for query: '{query}'")
    
    try:
        retrieved_docs: List[Document] = vector_store.similarity_search(query, k=k)
        
        if retrieved_docs:
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\nContent: {doc.page_content[:500]}")
                for doc in retrieved_docs
            )
            logger.info(f"   ✓ Found {len(retrieved_docs)} documents")
            return f"Retrieved relevant information:\n\n{serialized}"
        else:
            logger.warning(f"   ⚠ No documents found for query: {query}")
            return f"No relevant information found for: {query}"
    except Exception as e:
        logger.error(f"   ✗ Error in retrieve_context: {e}")
        return f"Error retrieving information: {str(e)}"
