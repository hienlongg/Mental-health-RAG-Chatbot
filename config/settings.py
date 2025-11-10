"""Application settings and environment configuration."""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    langsmith_api_key: str
    langsmith_tracing: bool = True
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_project: str

    openai_api_key: str = ""
    google_api_key: str

    # Paths
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    documents_dir: Path = data_dir / "documents"
    embeddings_dir: Path = data_dir / "embeddings"
    logs_dir: Path = project_root / "logs"

    # Model settings
    embedding_model: str = "models/gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash-lite"

    # Vector store
    vector_store_collection: str = "example_collection"
    vector_store_persist_dir: str = "./chroma_langchain_db"

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
