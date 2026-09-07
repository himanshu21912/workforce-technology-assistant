from typing import Any

from pydantic import BaseModel, Field


class ToolError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(
        default_factory=dict,
    )


class ToolResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: ToolError | None = None
    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )