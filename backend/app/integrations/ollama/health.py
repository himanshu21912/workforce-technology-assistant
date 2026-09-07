from app.integrations.ollama.client import OllamaClient
from app.schemas.health import DependencyHealth


async def check_ollama() -> DependencyHealth:
    try:
        async with OllamaClient() as client:
            is_available = await client.check_health()

        if not is_available:
            return DependencyHealth(
                status="unavailable",
                message="Ollama health check failed.",
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