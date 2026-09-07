import asyncio
import json

from app.integrations.redis import (
    close_redis_client,
    get_redis_client,
)
from app.memory import RedisHistoryRepository
from app.services import SessionService


async def main() -> None:
    redis_client = get_redis_client()

    repository = RedisHistoryRepository(redis_client)

    service = SessionService.from_repository(repository)

    session = await service.create_session(
        title="Phase 5 memory test"
    )

    session_id = str(session.session_id)

    print()
    print("CREATED SESSION")
    print("=" * 80)
    print(
        json.dumps(
            session.model_dump(mode="json"),
            indent=2,
        )
    )

    await service.add_user_message(
        session_id=session_id,
        content="Find employees who know Python.",
    )

    await service.add_assistant_message(
        session_id=session_id,
        content=(
            "Ravi, Ananya, Vikram, and Meera know Python."
        ),
        metadata={
            "source": "postgresql",
            "tools_used": [
                "search_employees",
            ],
        },
    )

    await service.add_user_message(
        session_id=session_id,
        content="Which one has the most experience?",
    )

    await service.add_assistant_message(
        session_id=session_id,
        content="Ravi has the most overall experience.",
        metadata={
            "source": "postgresql",
            "tools_used": [
                "get_employee_details",
            ],
        },
    )

    history = await service.get_session_history(
        session_id
    )

    print()
    print("SESSION HISTORY")
    print("=" * 80)
    print(
        json.dumps(
            history.model_dump(mode="json"),
            indent=2,
        )
    )

    sessions = await service.list_sessions()

    print()
    print("ACTIVE SESSIONS")
    print("=" * 80)
    print(
        json.dumps(
            [
                item.model_dump(mode="json")
                for item in sessions
            ],
            indent=2,
        )
    )

    deleted = await service.delete_session(
        session_id
    )

    print()
    print("SESSION DELETED")
    print("=" * 80)
    print(deleted)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(close_redis_client())