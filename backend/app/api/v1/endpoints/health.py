import asyncio

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import AsyncSessionFactory
from app.integrations.ollama import check_ollama
from app.integrations.redis import check_redis
from app.schemas.health import (
    DependencyHealth,
    HealthResponse,
    ServiceInformation,
)


router = APIRouter()


async def check_postgres() -> DependencyHealth:
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(
                text("SELECT 1")
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


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API and dependency health",
)
async def get_health() -> HealthResponse:
    settings = get_settings()

    (
        postgres_health,
        redis_health,
        ollama_health,
    ) = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_ollama(),
    )

    dependencies = {
        "postgres": postgres_health,
        "redis": redis_health,
        "ollama": ollama_health,
    }

    all_dependencies_connected = all(
        dependency.status == "connected"
        for dependency in dependencies.values()
    )

    return HealthResponse(
        status=(
            "ok"
            if all_dependencies_connected
            else "degraded"
        ),
        service=ServiceInformation(
            name=settings.app_name,
            version=settings.app_version,
            environment=settings.environment,
        ),
        dependencies=dependencies,
    )