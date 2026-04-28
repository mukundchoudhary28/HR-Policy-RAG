
config_code = """
Application configuration using Pydantic Settings.
Handles env vars, validation, and multi-environment support.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra env vars without error
    )
    
    # =========================================================================
    # APP CONFIG
    # =========================================================================
    app_name: str = Field(default="HR Policy RAG API", description="API title")
    app_version: str = Field(default="1.0.0", description="API version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment"
    )

    # =========================================================================
    # OPENAI / LLM
    # =========================================================================
    openai_api_key: str = Field(description="OpenAI API key", validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", description="Chat model")
    openai_temperature: float = Field(default=0.2, ge=0, le=2, description="Sampling temp")
    openai_max_tokens: int = Field(default=2000, ge=1, description="Max response tokens")
    
    # Fallback for cost-saving
    fallback_model: str = Field(default="gpt-3.5-turbo", description="Fallback chat model")
    
    # =========================================================================
    # EMBEDDINGS
    # =========================================================================
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model"
    )
    embedding_device: Literal["cpu", "cuda"] = Field(default="cpu", description="Device")
    embedding_batch_size: int = Field(default=32, ge=1, description="Batch size")
    
    # =========================================================================
    # VECTOR DB (Chroma)
    # =========================================================================
    chroma_persist_dir: Path = Field(
        default=Path("./chroma_db"),
        description="Chroma persistence directory"
    )
    chroma_collection: str = Field(default="document_chunks", description="Collection name")
    chroma_anonymized_telemetry: bool = Field(default=False, description="Chroma telemetry")
    
    @field_validator("chroma_persist_dir", mode="before")
    @classmethod
    def parse_chroma_path(cls, v):
        """Ensure path is Path object."""
        return Path(v) if isinstance(v, str) else v
    
    # =========================================================================
    # RAG / RETRIEVAL
    # =========================================================================
    chunk_size: int = Field(default=900, ge=100, le=2000, description="Text chunk size")
    chunk_overlap: int = Field(default=75, ge=0, le=500, description="Chunk overlap")
    top_k: int = Field(default=5, ge=1, le=20, description="Retrieved chunks per query")
    similarity_threshold: float = Field(
        default=0.6,
        ge=0,
        le=1,
        description="Minimum similarity score"
    )
    
    # Hybrid search weights (Day 3)
    vector_weight: float = Field(default=0.7, ge=0, le=1, description="Vector search weight")
    keyword_weight: float = Field(default=0.3, ge=0, le=1, description="Keyword search weight")
    
    # Reranker (Day 5)
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder for reranking"
    )
    reranker_top_k: int = Field(default=3, ge=1, description="Final chunks after rerank")
    use_reranker: bool = Field(default=True, description="Enable reranking")
    
    # =========================================================================
    # DOCUMENT PROCESSING
    # =========================================================================
    documents_dir: Path = Field(
        default=Path("./data/documents"),
        description="Upload directory"
    )
    max_file_size_mb: int = Field(default=50, ge=1, description="Max upload size")
    # allowed_extensions: List[str] = Field(
    #     default_factory=lambda: [".docx", ".pdf", ".txt", ".md"],
    #     description="Allowed file types"
    # )

    HASH_FILE_PATH: Path = Field(
        default=Path("./data/manifest.json"),
        description="File hash manifest for change detection"
    )
    
    @field_validator("documents_dir", mode="before")
    @classmethod
    def parse_docs_path(cls, v):
        """Ensure path is Path object."""
        return Path(v) if isinstance(v, str) else v
    
    
    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    @property
    def max_file_size_bytes(self) -> int:
        """Max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def openai_kwargs(self) -> dict:
        """Common kwargs for OpenAI calls."""
        return {
            "temperature": self.openai_temperature,
            "max_tokens": self.openai_max_tokens,
        }
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Usage:
        from src.core.config import get_settings
        settings = get_settings()
        print(settings.openai_model)
    """
    settings = Settings()
    settings.ensure_directories()
    return settings


# Convenience export for direct import
settings = get_settings()

