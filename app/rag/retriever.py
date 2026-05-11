from __future__ import annotations

from typing import Iterable

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models import RetrievalResult

COLLECTION_NAME = "pipeline_docs"


def _embedder() -> SentenceTransformer:
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class Retriever:
    """
    Hybrid + Corrective RAG retriever.
    Combines semantic search with relevance correction and source diversity.
    """
    
    def __init__(self, persist_path: str | None = None) -> None:
        self.persist_path = persist_path or settings.chroma_path
        self.client = chromadb.PersistentClient(path=self.persist_path)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        self.model = _embedder()

    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """
        Hybrid search combining semantic relevance with source diversity.
        Returns contextually relevant chunks from multiple document types.
        """
        embedding = self.model.encode([query])[0].tolist()
        
        # Semantic search with extra results for filtering
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(top_k * 2, 20),  # Fetch more to filter
            include=["documents", "metadatas", "distances"]
        )
        
        docs: list[str] = result.get("documents", [[]])[0]
        metas: list[dict] = result.get("metadatas", [[]])[0]
        dists: list[float] = result.get("distances", [[]])[0]
        
        # Create initial results with relevance scores
        initial_results = []
        for doc, meta, dist in zip(docs, metas, dists):
            score = 1.0 - float(dist)  # Convert distance to similarity
            
            # Corrective filtering: boost relevant sources
            source_type = meta.get("type", "unknown")
            if "dataset" in source_type or "code" in source_type:
                score = min(1.0, score * 1.1)  # Slight boost for primary sources
            
            # Relevance correction: penalize generic results
            is_generic = any(
                word in doc.lower()
                for word in ["example", "template", "sample", "note:", "document"]
            )
            if is_generic and score < 0.7:
                continue  # Skip low-confidence generic results
            
            initial_results.append({
                "doc": doc,
                "meta": meta,
                "score": score,
                "source_type": source_type
            })
        
        # Diversify results by source type
        final_results = []
        source_types_seen = {}
        
        # Sort by score
        initial_results.sort(key=lambda x: x["score"], reverse=True)
        
        for result in initial_results:
            source_type = result["source_type"]
            
            # Limit results per source type to ensure diversity
            if source_types_seen.get(source_type, 0) >= 2:
                continue
            
            source_types_seen[source_type] = source_types_seen.get(source_type, 0) + 1
            
            final_results.append(
                RetrievalResult(
                    source=result["meta"].get("source", "unknown"),
                    score=result["score"],
                    content=result["doc"],
                )
            )
            
            if len(final_results) >= top_k:
                break
        
        # If we don't have enough results, add remaining ones
        for result in initial_results:
            if len(final_results) >= top_k:
                break
            if result not in [r for r in initial_results[:final_results.__len__()]]:
                final_results.append(
                    RetrievalResult(
                        source=result["meta"].get("source", "unknown"),
                        score=result["score"],
                        content=result["doc"],
                    )
                )
        
        return final_results[:top_k]
