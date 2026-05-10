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
    def __init__(self, persist_path: str | None = None) -> None:
        self.persist_path = persist_path or settings.chroma_path
        self.client = chromadb.PersistentClient(path=self.persist_path)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        self.model = _embedder()

    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        embedding = self.model.encode([query])[0].tolist()
        result = self.collection.query(
            query_embeddings=[embedding], n_results=top_k, include=["documents", "metadatas", "distances"]
        )
        docs: Iterable[str] = result.get("documents", [[]])[0]
        metas: Iterable[dict] = result.get("metadatas", [[]])[0]
        dists: Iterable[float] = result.get("distances", [[]])[0]
        items: list[RetrievalResult] = []
        for doc, meta, dist in zip(docs, metas, dists):
            items.append(
                RetrievalResult(
                    source=meta.get("source", "unknown"),
                    score=1.0 - float(dist),
                    content=doc,
                )
            )
        return items
