from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from app.agent import AgentOrchestrator
from app.integrations.ollama import OllamaClient
from app.integrations.redis import get_redis_client
from app.memory import RedisHistoryRepository
from app.semantic_cache.cache_service import (
    SemanticCacheService,
)
from app.semantic_cache.factory import (
    create_semantic_cache_service,
)
from app.services import ChatService, SessionService


def get_session_service() -> SessionService:
    repository = RedisHistoryRepository(
        get_redis_client()
    )

    return SessionService.from_repository(
        repository
    )


async def get_semantic_cache_service(
) -> AsyncGenerator[SemanticCacheService, None]:
    ollama_client = OllamaClient()

    try:
        yield create_semantic_cache_service(
            ollama_client
        )
    finally:
        await ollama_client.close()


def get_chat_service(
    session_service: Annotated[
        SessionService,
        Depends(get_session_service),
    ],
    semantic_cache_service: Annotated[
        SemanticCacheService,
        Depends(get_semantic_cache_service),
    ],
) -> ChatService:
    return ChatService(
        session_service=session_service,
        semantic_cache_service=(
            semantic_cache_service
        ),
        agent_orchestrator=AgentOrchestrator(),
    )


SessionServiceDependency = Annotated[
    SessionService,
    Depends(get_session_service),
]

SemanticCacheServiceDependency = Annotated[
    SemanticCacheService,
    Depends(get_semantic_cache_service),
]

ChatServiceDependency = Annotated[
    ChatService,
    Depends(get_chat_service),
]