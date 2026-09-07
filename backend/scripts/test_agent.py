import asyncio
import json
from typing import Any

from app.agent import (
    AgentExecutionResult,
    AgentOrchestrator,
)
from app.db.session import close_database_engine
from app.integrations.redis import close_redis_client
from app.schemas.message import (
    ConversationMessage,
    MessageRole,
)


def print_result(
    title: str,
    result: AgentExecutionResult,
) -> None:
    """
    Print a simplified agent result for manual verification.
    """

    output: dict[str, Any] = {
        "answer": result.answer,
        "source": result.source,
        "tools_used": result.tools_used,
    }

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


async def test_general_question(
    orchestrator: AgentOrchestrator,
) -> None:
    result = await orchestrator.run(
        question="What is FastAPI?",
        context=(
            "Explain it briefly for a beginner."
        ),
    )

    print_result(
        "GENERAL KNOWLEDGE QUESTION",
        result,
    )


async def test_internal_database_question(
    orchestrator: AgentOrchestrator,
) -> None:
    result = await orchestrator.run(
        question=(
            "Search the internal employee database for "
            "employees who know Python and show their roles."
        ),
    )

    print_result(
        "INTERNAL POSTGRESQL QUESTION",
        result,
    )


async def test_external_github_question(
    orchestrator: AgentOrchestrator,
) -> None:
    result = await orchestrator.run(
        question=(
            "Using current GitHub data, find three popular "
            "public FastAPI repositories written in Python."
        ),
    )

    print_result(
        "EXTERNAL GITHUB MCP QUESTION",
        result,
    )


async def test_multi_source_question(
    orchestrator: AgentOrchestrator,
) -> None:
    result = await orchestrator.run(
        question=(
            "Find internal employees with FastAPI experience "
            "and recommend a suitable current public GitHub "
            "repository for them to study."
        ),
    )

    print_result(
        "MULTI-SOURCE QUESTION",
        result,
    )


async def test_follow_up_question(
    orchestrator: AgentOrchestrator,
) -> None:
    conversation_history = [
        ConversationMessage(
            role=MessageRole.USER,
            content=(
                "Find employees who know Python."
            ),
        ),
        ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=(
                "Ravi, Ananya, Vikram, and Meera know Python."
            ),
            metadata={
                "source": "postgresql",
                "tools_used": [
                    "search_employees",
                ],
            },
        ),
    ]

    result = await orchestrator.run(
        question=(
            "Which one is a backend engineer?"
        ),
        conversation_history=conversation_history,
    )

    print_result(
        "FOLLOW-UP QUESTION",
        result,
    )


async def main() -> None:
    orchestrator = AgentOrchestrator()

    await test_general_question(
        orchestrator
    )

    await test_internal_database_question(
        orchestrator
    )

    await test_external_github_question(
        orchestrator
    )

    await test_multi_source_question(
        orchestrator
    )

    await test_follow_up_question(
        orchestrator
    )


async def run() -> None:
    try:
        await main()
    finally:
        await close_redis_client()
        await close_database_engine()


if __name__ == "__main__":
    asyncio.run(run())