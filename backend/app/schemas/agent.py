from typing import Literal

from pydantic import BaseModel, Field


AgentSource = Literal[
    "llm",
    "postgresql",
    "github_mcp",
    "multi_source",
]


class AgentResponse(BaseModel):
    answer: str = Field(
        min_length=1,
    )
    tools_used: list[str] = Field(
        default_factory=list,
    )
    source: AgentSource