"""
Application configuration loaded from environment variables.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- GROQ LLM ---
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # --- Database Paths ---
    SQLITE_DB_PATH: str = "data/ecommerce.db"
    CHAT_DB_PATH: str = "data/chat_history.db"

    # --- ChromaDB ---
    CHROMA_PERSIST_DIR: str = "data/chroma_db"

    # --- PDF Storage ---
    PDF_STORAGE_DIR: str = "data/uploaded_pdfs"

    # --- Server ---
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501

    # --- Embedding Model ---
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # --- RAG Settings ---
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    # --- Refund Policy ---
    REFUND_WINDOW_DAYS: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def sqlite_db_url(self) -> str:
        db_path = PROJECT_ROOT / self.SQLITE_DB_PATH
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"

    @property
    def chat_db_url(self) -> str:
        db_path = PROJECT_ROOT / self.CHAT_DB_PATH
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"

    @property
    def chroma_path(self) -> str:
        path = PROJECT_ROOT / self.CHROMA_PERSIST_DIR
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @property
    def pdf_path(self) -> str:
        path = PROJECT_ROOT / self.PDF_STORAGE_DIR
        path.mkdir(parents=True, exist_ok=True)
        return str(path)


# Singleton settings instance
settings = Settings()
