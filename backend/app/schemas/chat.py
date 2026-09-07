from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    session_id: str = Field(
        min_length=36,
        max_length=36,
        description=(
            "UUID of the conversation session that owns "
            "the question and semantic-cache entries."
        ),
    )

    question: str = Field(
        min_length=1,
        max_length=10000,
        description="The question asked by the user.",
    )

    context: str | None = Field(
        default=None,
        max_length=10000,
        description=(
            "Optional additional context or answer instructions."
        ),
    )

    @field_validator("session_id", "question")
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "The value cannot be empty."
            )

        return normalized

    @field_validator("context")
    @classmethod
    def normalize_optional_context(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class AskResponse(BaseModel):
    session_id: str
    answer: str

    cache_hit: bool = False

    similarity_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    source: str

    tools_used: list[str] = Field(
        default_factory=list,
    )

    model_name: str | None = None


class DeleteSessionResponse(BaseModel):
    session_id: str
    session_deleted: bool
    semantic_cache_entries_deleted: int