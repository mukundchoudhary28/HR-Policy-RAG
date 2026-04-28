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


# # For hash tracking (non-cacheable, needs state)
# class HashStore:
#     """Simple hash tracking singleton."""
#     _instance = None
#     _hashes = {}
    
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._load()
#         return cls._instance
    
#     @classmethod
#     def _load(cls):
#         from utils.reindexing import load_hashes
#         cls._hashes = load_hashes()
    
#     def get(self, key, default=None):
#         return self._hashes.get(key, default)
    
#     def set(self, key, value):
#         self._hashes[key] = value
#         from utils.reindexing import save_hashes
#         save_hashes(self._hashes)
    
#     def all(self):
#         return self._hashes


# def get_hash_store():
#     """Get hash store instance."""
#     return HashStore()