from app.models import RetrievalResult
from app.services.chat_service import ChatService


class DummyRetriever:
    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        return [
            RetrievalResult(
                source="dummy.md",
                score=0.9,
                content=f"retrieved context for: {query}",
            )
        ]


def test_chat_service_returns_response() -> None:
    service = ChatService(retriever=DummyRetriever())
    result = service.chat("what is lineage?", run_quality_check=False)
    assert result.answer
    assert len(result.citations) == 1


def test_chat_service_runs_action() -> None:
    service = ChatService(retriever=DummyRetriever())
    result = service.chat("run checks", run_quality_check=True)
    assert result.quality_check_result is not None
