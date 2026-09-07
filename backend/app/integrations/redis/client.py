from redis.asyncio import Redis

from app.core.config import get_settings


settings = get_settings()


redis_client: Redis = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=settings.redis_socket_timeout,
    socket_timeout=settings.redis_socket_timeout,
    max_connections=settings.redis_max_connections,
    health_check_interval=30,
)


def get_redis_client() -> Redis:
    return redis_client


async def close_redis_client() -> None:
    await redis_client.aclose()