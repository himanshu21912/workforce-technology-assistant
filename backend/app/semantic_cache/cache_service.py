from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.integrations.ollama import EmbeddingService
from app.schemas.semantic_cache import (
    SemanticCacheEntry,
    SemanticCacheMatch,
)
from app.semantic_cache.cache_policy import SemanticCachePolicy
from app.semantic_cache.cache_repository import (
    RedisSemanticCacheRepository,
)


class SemanticCacheService:
    def __init__(
        self,
        *,
        repository: RedisSemanticCacheRepository,
        embedding_service: EmbeddingService,
        policy: SemanticCachePolicy,
    ) -> None:
        self._repository = repository
        self._embedding_service = embedding_service
        self._policy = policy
        self._settings = get_settings()

    async def lookup(
        self,
        *,
        session_id: str,
        question: str,
    ) -> SemanticCacheMatch:
        self._validate_session_id(session_id)

        normalized_question = self._normalize_question(
            question
        )

        if self._policy.should_bypass_lookup(
            normalized_question
        ):
            return SemanticCacheMatch(
                cache_hit=False,
                similarity_score=None,
                entry=None,
            )

        embedding = await self._embedding_service.embed_text(
            normalized_question
        )

        candidates = await self._repository.search(
            session_id=session_id,
            embedding=embedding,
            count=self._settings.semantic_cache_max_results,
        )

        for candidate in candidates:
            if not self._policy.is_similarity_match(
                candidate.similarity_score
            ):
                continue

            entry = await self._repository.get_entry(
                session_id=session_id,
                entry_id=candidate.entry_id,
            )

            if entry is None:
                await self._repository.remove_entry(
                    session_id=session_id,
                    entry_id=candidate.entry_id,
                )
                continue

            if str(entry.session_id) != session_id:
                continue

            return SemanticCacheMatch(
                cache_hit=True,
                similarity_score=(
                    candidate.similarity_score
                ),
                entry=entry,
            )

        return SemanticCacheMatch(
            cache_hit=False,
            similarity_score=None,
            entry=None,
        )

    async def store(
        self,
        *,
        session_id: str,
        question: str,
        answer: str,
        source: str,
        tools_used: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SemanticCacheEntry | None:
        validated_session_id = self._validate_session_id(
            session_id
        )

        normalized_question = self._normalize_question(
            question
        )
        normalized_answer = answer.strip()
        normalized_source = source.strip()

        if not normalized_answer:
            raise ValueError(
                "Answer cannot be empty."
            )

        if not normalized_source:
            raise ValueError(
                "Source cannot be empty."
            )

        if not self._policy.should_store_response(
            question=normalized_question,
            answer=normalized_answer,
            source=normalized_source,
        ):
            return None

        embedding = await self._embedding_service.embed_text(
            normalized_question
        )

        entry = SemanticCacheEntry(
            session_id=validated_session_id,
            question=normalized_question,
            answer=normalized_answer,
            source=normalized_source,
            tools_used=tools_used or [],
            model_name=self._settings.ollama_chat_model,
            metadata=metadata or {},
        )

        await self._repository.store(
            entry=entry,
            embedding=embedding,
        )

        return entry

    async def clear_session(
        self,
        session_id: str,
    ) -> int:
        self._validate_session_id(session_id)

        return await self._repository.clear_session(
            session_id
        )

    async def count_entries(
        self,
        session_id: str,
    ) -> int:
        self._validate_session_id(session_id)

        return await self._repository.count_entries(
            session_id
        )

    @staticmethod
    def _normalize_question(
        question: str,
    ) -> str:
        normalized_question = " ".join(
            question.strip().split()
        )

        if not normalized_question:
            raise ValueError(
                "Question cannot be empty."
            )

        return normalized_question

    @staticmethod
    def _validate_session_id(
        session_id: str,
    ) -> UUID:
        try:
            parsed_session_id = UUID(session_id)
        except (TypeError, ValueError) as exception:
            raise ValueError(
                "Session ID must be a valid UUID."
            ) from exception

        if str(parsed_session_id) != session_id.lower():
            raise ValueError(
                "Session ID must use the canonical UUID format."
            )

        return parsed_session_id