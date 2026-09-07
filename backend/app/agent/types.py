from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentExecutionResult:
    answer: str
    tools_used: list[str] = field(
        default_factory=list
    )
    source: str = "llm"
    raw_messages: list[Any] = field(
        default_factory=list
    )