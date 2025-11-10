"""PDF document loader module."""
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain_core.documents import Document


def load_pdf_documents(file_path: str | Path) -> List[Document]:
    """
    Load documents from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of Document objects
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    print(f"Loaded {len(docs)} pages from {file_path.name}")
    return docs
