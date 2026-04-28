"""
Shared dependencies and resource management.
"""

from functools import lru_cache
from chromadb import PersistentClient
from langchain_huggingface import HuggingFaceEmbeddings

from src.core.config import get_settings


@lru_cache()
def get_chroma_client():
    """Singleton Chroma client."""
    settings = get_settings()
    return PersistentClient(path=str(settings.chroma_persist_dir))


@lru_cache()
def get_chroma_collection():
    """Singleton collection."""
    client = get_chroma_client()
    settings = get_settings()
    return client.get_or_create_collection(name=settings.chroma_collection)


@lru_cache()
def get_embedding_model():
    """Singleton embedding model."""
    settings = get_settings()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device}
    )
