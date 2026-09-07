from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from app.schemas.message import ConversationMessage


class CreateSessionInput(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=150,
    )

    @field_validator("title")
    @classmethod
    def normalize_title(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = " ".join(value.strip().split())

        return cleaned_value or None


class ChatSession(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    title: str = Field(
        min_length=1,
        max_length=150,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    message_count: int = Field(
        default=0,
        ge=0,
    )


class SessionHistory(BaseModel):
    session: ChatSession
    messages: list[ConversationMessage]