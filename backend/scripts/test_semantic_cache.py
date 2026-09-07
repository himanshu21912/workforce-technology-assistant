import asyncio
import json

from app.integrations.ollama import OllamaClient
from app.integrations.redis import (
    close_redis_client,
    get_redis_client,
)
from app.memory import RedisHistoryRepository
from app.semantic_cache.factory import (
    create_semantic_cache_service,
)
from app.services import SessionService


def print_json(
    title: str,
    value: object,
) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


async def main() -> None:
    redis_client = get_redis_client()

    history_repository = RedisHistoryRepository(
        redis_client
    )

    session_service = SessionService.from_repository(
        history_repository
    )

    primary_session = await session_service.create_session(
        title="Phase 6 semantic cache test"
    )

    isolated_session = await session_service.create_session(
        title="Phase 6 isolation test"
    )

    primary_session_id = str(
        primary_session.session_id
    )
    isolated_session_id = str(
        isolated_session.session_id
    )

    async with OllamaClient() as ollama_client:
        semantic_cache = create_semantic_cache_service(
            ollama_client
        )

        try:
            stored_entry = await semantic_cache.store(
                session_id=primary_session_id,
                question=(
                    "How many employees work in Engineering?"
                ),
                answer=(
                    "There are 3 employees in Engineering."
                ),
                source="postgresql",
                tools_used=[
                    "get_employee_statistics",
                ],
                metadata={
                    "test": True,
                },
            )

            print_json(
                "STORED CACHE ENTRY",
                (
                    stored_entry.model_dump(mode="json")
                    if stored_entry is not None
                    else None
                ),
            )

            exact_match = await semantic_cache.lookup(
                session_id=primary_session_id,
                question=(
                    "How many employees work in Engineering?"
                ),
            )

            print_json(
                "EXACT CACHE MATCH",
                exact_match.model_dump(mode="json"),
            )

            semantic_match = await semantic_cache.lookup(
                session_id=primary_session_id,
                question=(
                    "What is the employee count in the "
                    "Engineering department?"
                ),
            )

            print_json(
                "SEMANTIC CACHE MATCH",
                semantic_match.model_dump(mode="json"),
            )

            isolated_result = await semantic_cache.lookup(
                session_id=isolated_session_id,
                question=(
                    "How many employees work in Engineering?"
                ),
            )

            print_json(
                "DIFFERENT SESSION RESULT",
                isolated_result.model_dump(mode="json"),
            )

            freshness_result = await semantic_cache.lookup(
                session_id=primary_session_id,
                question=(
                    "How many employees currently work "
                    "in Engineering?"
                ),
            )

            print_json(
                "FRESHNESS BYPASS RESULT",
                freshness_result.model_dump(mode="json"),
            )

            primary_cache_count = (
                await semantic_cache.count_entries(
                    primary_session_id
                )
            )

            print_json(
                "PRIMARY SESSION CACHE COUNT",
                {
                    "count": primary_cache_count,
                },
            )

        finally:
            await semantic_cache.clear_session(
                primary_session_id
            )

            await semantic_cache.clear_session(
                isolated_session_id
            )

            await session_service.delete_session(
                primary_session_id
            )

            await session_service.delete_session(
                isolated_session_id
            )


async def run() -> None:
    try:
        await main()
    finally:
        await close_redis_client()


if __name__ == "__main__":
    asyncio.run(run())