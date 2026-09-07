from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class SemanticCacheEntry(BaseModel):
    entry_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    question: str = Field(
        min_length=1,
        max_length=10000,
    )
    answer: str = Field(
        min_length=1,
        max_length=50000,
    )
    source: str = Field(
        min_length=1,
        max_length=100,
    )
    tools_used: list[str] = Field(
        default_factory=list,
    )
    model_name: str = Field(
        min_length=1,
        max_length=200,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("question", "answer", "source", "model_name")
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Semantic-cache text fields cannot be empty."
            )

        return normalized


class SemanticCacheMatch(BaseModel):
    cache_hit: bool
    similarity_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    entry: SemanticCacheEntry | None = None


class SemanticCacheLookupInput(BaseModel):
    session_id: UUID
    question: str = Field(
        min_length=1,
        max_length=10000,
    )

    @field_validator("question")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())

        if not normalized:
            raise ValueError(
                "Question cannot be empty."
            )

        return normalized