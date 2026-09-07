from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import AsyncSessionFactory
from app.schemas.health import (
    DependencyHealth,
    HealthResponse,
    ServiceInformation,
)


router = APIRouter()


async def check_postgres() -> DependencyHealth:
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))

        return DependencyHealth(
            status="connected",
        )
    except Exception as exc:
        return DependencyHealth(
            status="unavailable",
            message=type(exc).__name__,
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API and dependency health",
)
async def get_health() -> HealthResponse:
    settings = get_settings()
    postgres_health = await check_postgres()

    overall_status = (
        "ok"
        if postgres_health.status == "connected"
        else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        service=ServiceInformation(
            name=settings.app_name,
            version=settings.app_version,
            environment=settings.environment,
        ),
        dependencies={
            "postgres": postgres_health,
        },
    )