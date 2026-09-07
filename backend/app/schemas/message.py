from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    role: MessageRole
    content: str = Field(
        min_length=1,
        max_length=50000,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Message content cannot be empty."
            )

        return cleaned_value


class AddMessageInput(BaseModel):
    role: MessageRole
    content: str = Field(
        min_length=1,
        max_length=50000,
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Message content cannot be empty."
            )

        return cleaned_value