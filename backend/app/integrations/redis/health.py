from app.integrations.redis.client import (
    get_redis_client,
)
from app.schemas.health import DependencyHealth


async def check_redis() -> DependencyHealth:
    client = get_redis_client()

    try:
        is_available = await client.ping()

        if not is_available:
            return DependencyHealth(
                status="unavailable",
                message="Redis ping returned an invalid response.",
            )

        return DependencyHealth(
            status="connected",
            message=None,
        )

    except Exception as exception:
        return DependencyHealth(
            status="unavailable",
            message=type(exception).__name__,
        )