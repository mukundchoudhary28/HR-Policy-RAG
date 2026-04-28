"""
Cross-encoder reranker for improving retrieval results.
"""

from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from src.core.config import get_settings
from langsmith import traceable

settings = get_settings()


class CrossEncoderReranker:
    """Reranks candidate documents using a cross-encoder model."""
    
    _instance = None  # Singleton instance
    _model = None     # Cached model
    
    def __new__(cls, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._model_name = model_name
            cls._model = CrossEncoder(model_name)
            print(f"CrossEncoder loaded: {model_name}")
        return cls._instance
    
    @traceable(name="Reranker")
    def rerank(
        self, 
        query: str, 
        candidates: List[Dict[str, Any]], 
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidates by relevance to query.
        
        Args:
            query: User query string
            candidates: List of candidate docs with at least "content" key
            top_k: Return only top_k results (None = return all reranked)
        
        Returns:
            Candidates sorted by reranker score (descending)
        """
        if not candidates:
            return []
        
        if top_k is None:
            top_k = settings.reranker_top_k
        
        # Build query-document pairs for cross-encoder
        pairs = [[query, hit["content"]] for hit in candidates]
        
        # Get relevance scores from cross-encoder
        scores = self._model.predict(pairs)
        
        # Attach scores to candidates
        for hit, score in zip(candidates, scores):
            hit["reranker_score"] = float(score)
        
        # Sort by reranker score descending
        candidates.sort(key=lambda x: x["reranker_score"], reverse=True)
        
        if top_k:
            return candidates[:top_k]
        return candidates