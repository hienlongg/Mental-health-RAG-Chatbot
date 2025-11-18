"""RAG pipeline initialization and utilities."""
from rag.loaders.pdf_loader import load_pdf_documents
from rag.embeddings.vectorstore import initialize_embeddings, initialize_vector_store
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Main RAG pipeline orchestrator."""

    def __init__(self):
        """Initialize RAG pipeline with settings."""
        self.settings = get_settings()
        self.embeddings = None
        self.vector_store = None
        self.model = None

    def setup_embeddings(self) -> None:
        """Initialize embeddings."""
        self.embeddings = initialize_embeddings(self.settings.embedding_model)

    def setup_vector_store(self, persist_dir: Optional[str] = None) -> None:
        """Initialize vector store."""
        if not self.embeddings:
            self.setup_embeddings()

        persist_dir = persist_dir or self.settings.vector_store_persist_dir
        self.vector_store = initialize_vector_store(
            self.embeddings,
            collection_name=self.settings.vector_store_collection,
            persist_directory=persist_dir,
        )

    def setup_chat_model(self) -> None:
        """Initialize chat model."""
        self.model = ChatGoogleGenerativeAI(model=self.settings.chat_model)
        print(f"✓ Chat model initialized: {self.settings.chat_model}")

    def load_and_index_documents(self, file_path: str | Path) -> None:
        """Load documents and add to vector store."""
        if not self.vector_store:
            self.setup_vector_store()

        docs = load_pdf_documents(file_path)
        self.vector_store.add_documents(docs)
        print(f"✓ {len(docs)} documents indexed")

    def initialize_all(self) -> None:
        """Initialize all components."""
        print("🚀 Initializing RAG pipeline...")
        self.setup_embeddings()
        self.setup_vector_store()
        self.setup_chat_model()
        print("✓ RAG pipeline ready!")
