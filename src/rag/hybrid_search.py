"""
Hybrid retrieval: Vector (Chroma) + BM25 keyword search.
"""

from typing import List, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi

from src.core.dependencies import get_chroma_collection
from src.core.config import get_settings
from src.rag.reranker import CrossEncoderReranker

settings = get_settings()


class HybridRetriever:
    """Combines vector similarity with BM25 keyword search."""
    
    def __init__(self, reranker: Any = None):
        self.collection = get_chroma_collection()
        self.documents_cache = []  # For BM25
        self.metadata_cache = []
        self.bm25 = None
        self._build_bm25_index()

        self.reranker = reranker if reranker else CrossEncoderReranker()

    
    def _build_bm25_index(self):
        """Build BM25 index from all documents in Chroma."""
        results = self.collection.get()
        
        if not results["documents"]:
            self.documents_cache = []
            self.metadata_cache = []
            self.bm25 = None
            return
        
        self.documents_cache = results["documents"]
        self.metadata_cache = results["metadatas"]
        tokenized = [doc.lower().split() for doc in self.documents_cache]
        self.bm25 = BM25Okapi(tokenized)


    def merge_results(self, list1, list2):
        merged = {}

        for item in list1 + list2:
            key = (item["content"], item["metadata"].get("file_name"))  
            # str() ensures dict is hashable

            if key not in merged:
                merged[key] = {
                    "content": item["content"],
                    "metadata": item.get("metadata", {}),
                    "vector_score": item.get("vector_score", 0),
                    "bm25_score": item.get("bm25_score", 0),
                }
            else:
                merged[key]["vector_score"] += item.get("vector_score", 0)
                merged[key]["bm25_score"] += item.get("bm25_score", 0)

        return list(merged.values())
    
    from langsmith import traceable

    @traceable(name="Retrieval")
    def search(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = None,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search: combine vector + BM25 scores.
        """
        if top_k is None:
            top_k = settings.top_k
        
        # Vector search via Chroma
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            where=filters if filters else None
        )
        
        vector_hits = []
        if vector_results["documents"][0]:
            for doc, meta, dist in zip(
                vector_results["documents"][0],
                vector_results["metadatas"][0],
                vector_results["distances"][0]
            ):
                # Convert distance to similarity score (1 = closest, 0 = farthest)
                score = 1 - (dist / 2)  # Normalize assuming cosine distance
                vector_hits.append({
                    "content": doc,
                    "metadata": meta,
                    "vector_score": score,
                    "bm25_score": 0,
                })
        
        # BM25 keyword search
        bm25_hits = []
        if self.bm25:
            tokenized_query = query.lower().split()
            scores = self.bm25.get_scores(tokenized_query)
            top_indices = np.argsort(scores)[-top_k*2:][::-1] # Outputs a list of indices sorted based on the highest scores. i.e. index0=highest score, index1=second-highest score

            
            for idx in top_indices:
                if scores[idx] > 0:
                    bm25_hits.append({
                        "content": self.documents_cache[idx],
                        "metadata": self.metadata_cache[idx],  # BM25 doesn't return metadata easily
                        "vector_score": 0,
                        "bm25_score": scores[idx] / max(scores) if max(scores) > 0 else 0,
                    })


            # Filtering only for latest documents:
            bm25_hits_new = []
            for hit in bm25_hits:
                if hit['metadata']['Is Latest'] == "Yes":
                    bm25_hits_new.append(hit)


        combined = self.merge_results(vector_hits,bm25_hits_new)
        # print(combined)
        

        # Calculate hybrid score
        for hit in combined:
            hit["hybrid_score"] = (
                settings.vector_weight * hit["vector_score"] +
                settings.keyword_weight * hit["bm25_score"]
            )
        
        # Sort by hybrid score and return top_k
        combined.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return self.reranker.rerank(query, combined[:top_k])
        # return combined[:top_k]


def get_hybrid_retriever(reranker: Any = None):
    """Get or create singleton retriever."""
    return HybridRetriever(reranker=reranker)