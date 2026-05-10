from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(min_length=1)


class RetrievalResult(BaseModel):
    source: str
    score: float
    content: str


class ChatRequest(BaseModel):
    message: str
    run_quality_check: bool = False


class ChatResponse(BaseModel):
    answer: str
    citations: list[RetrievalResult]
    quality_check_result: str | None = None
