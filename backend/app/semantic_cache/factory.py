from app.integrations.ollama import (
    EmbeddingService,
    OllamaClient,
)
from app.integrations.redis import get_redis_client
from app.semantic_cache.cache_policy import SemanticCachePolicy
from app.semantic_cache.cache_repository import (
    RedisSemanticCacheRepository,
)
from app.semantic_cache.cache_service import (
    SemanticCacheService,
)


def create_semantic_cache_service(
    ollama_client: OllamaClient,
) -> SemanticCacheService:
    redis_repository = RedisSemanticCacheRepository(
        get_redis_client()
    )

    embedding_service = EmbeddingService(
        ollama_client
    )

    cache_policy = SemanticCachePolicy()

    return SemanticCacheService(
        repository=redis_repository,
        embedding_service=embedding_service,
        policy=cache_policy,
    )