from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings
from app.schemas.semantic_cache import SemanticCacheEntry
from app.semantic_cache.cache_models import VectorSearchResult
from app.semantic_cache.keys import (
    semantic_entry_index_key,
    semantic_entry_key,
    semantic_vector_key,
)


class RedisSemanticCacheRepository:
    def __init__(self, client: Redis) -> None:
        self._client = client
        self._settings = get_settings()

    async def store(
        self,
        *,
        entry: SemanticCacheEntry,
        embedding: list[float],
    ) -> None:
        self._validate_embedding(embedding)

        session_id = str(entry.session_id)
        entry_id = str(entry.entry_id)

        vector_key = semantic_vector_key(session_id)
        metadata_key = semantic_entry_key(
            session_id,
            entry_id,
        )
        index_key = semantic_entry_index_key(session_id)

        try:
            await self._client.execute_command(
                "VADD",
                vector_key,
                "VALUES",
                len(embedding),
                *embedding,
                entry_id,
            )

            created_timestamp = entry.created_at.timestamp()

            async with self._client.pipeline(
                transaction=True
            ) as pipeline:
                pipeline.set(
                    metadata_key,
                    entry.model_dump_json(),
                    ex=self._settings.semantic_cache_ttl_seconds,
                )

                pipeline.zadd(
                    index_key,
                    {
                        entry_id: created_timestamp,
                    },
                )

                pipeline.expire(
                    index_key,
                    self._settings.semantic_cache_ttl_seconds,
                )

                pipeline.expire(
                    vector_key,
                    self._settings.semantic_cache_ttl_seconds,
                )

                await pipeline.execute()

        except Exception:
            await self._remove_vector_if_present(
                vector_key=vector_key,
                entry_id=entry_id,
            )
            raise

        await self._enforce_session_entry_limit(session_id)

    async def search(
        self,
        *,
        session_id: str,
        embedding: list[float],
        count: int,
    ) -> list[VectorSearchResult]:
        self._validate_embedding(embedding)

        if count < 1:
            raise ValueError(
                "Search result count must be greater than zero."
            )

        vector_key = semantic_vector_key(session_id)

        vector_set_exists = await self._client.exists(
            vector_key
        )

        if not vector_set_exists:
            return []

        raw_results: Any = await self._client.execute_command(
            "VSIM",
            vector_key,
            "VALUES",
            len(embedding),
            *embedding,
            "WITHSCORES",
            "COUNT",
            count,
        )

        if not raw_results:
            return []

        return self._parse_search_results(raw_results)

    async def get_entry(
        self,
        *,
        session_id: str,
        entry_id: str,
    ) -> SemanticCacheEntry | None:
        cached_value = await self._client.get(
            semantic_entry_key(
                session_id,
                entry_id,
            )
        )

        if cached_value is None:
            return None

        return SemanticCacheEntry.model_validate_json(
            cached_value
        )

    async def remove_entry(
        self,
        *,
        session_id: str,
        entry_id: str,
    ) -> None:
        vector_key = semantic_vector_key(session_id)
        metadata_key = semantic_entry_key(
            session_id,
            entry_id,
        )
        index_key = semantic_entry_index_key(session_id)

        async with self._client.pipeline(
            transaction=True
        ) as pipeline:
            pipeline.delete(metadata_key)
            pipeline.zrem(index_key, entry_id)
            pipeline.execute_command(
                "VREM",
                vector_key,
                entry_id,
            )

            await pipeline.execute()

    async def clear_session(
        self,
        session_id: str,
    ) -> int:
        vector_key = semantic_vector_key(session_id)
        index_key = semantic_entry_index_key(session_id)

        entry_ids = await self._client.zrange(
            index_key,
            0,
            -1,
        )

        keys_to_delete = [
            vector_key,
            index_key,
        ]

        keys_to_delete.extend(
            semantic_entry_key(
                session_id,
                entry_id,
            )
            for entry_id in entry_ids
        )

        deleted_count = await self._client.delete(
            *keys_to_delete
        )

        return int(deleted_count)

    async def count_entries(
        self,
        session_id: str,
    ) -> int:
        count = await self._client.zcard(
            semantic_entry_index_key(session_id)
        )

        return int(count)

    async def _enforce_session_entry_limit(
        self,
        session_id: str,
    ) -> None:
        index_key = semantic_entry_index_key(session_id)

        entry_count = await self._client.zcard(index_key)

        maximum_entries = (
            self._settings.semantic_cache_max_entries_per_session
        )

        overflow_count = entry_count - maximum_entries

        if overflow_count <= 0:
            return

        oldest_entry_ids = await self._client.zrange(
            index_key,
            0,
            overflow_count - 1,
        )

        for entry_id in oldest_entry_ids:
            await self.remove_entry(
                session_id=session_id,
                entry_id=entry_id,
            )

    async def _remove_vector_if_present(
        self,
        *,
        vector_key: str,
        entry_id: str,
    ) -> None:
        """
        Best-effort removal of a vector after a failed store.

        Errors are suppressed so the original failure is the
        exception that reaches the caller.
        """

        try:
            await self._client.execute_command(
                "VREM",
                vector_key,
                entry_id,
            )
        except Exception:
            return

    @staticmethod
    def _validate_embedding(
        embedding: list[float],
    ) -> None:
        if not embedding:
            raise ValueError(
                "Embedding cannot be empty."
            )

        if not all(
            isinstance(value, int | float)
            for value in embedding
        ):
            raise ValueError(
                "Embedding contains invalid values."
            )

    @staticmethod
    def _parse_search_results(
        raw_results: Any,
    ) -> list[VectorSearchResult]:
        """
        Normalize a "VSIM ... WITHSCORES" reply.

        Redis returns entry/score pairs, but the shape depends on
        the negotiated RESP protocol: a mapping of entry id to
        score under RESP3, and a flat [id, score, id, score, ...]
        array under RESP2. Both are accepted.
        """

        if isinstance(raw_results, dict):
            scored_entries = list(raw_results.items())

        elif isinstance(raw_results, (list, tuple)):
            if len(raw_results) % 2 != 0:
                raise ValueError(
                    "Redis returned an invalid vector search result."
                )

            scored_entries = [
                (
                    raw_results[index],
                    raw_results[index + 1],
                )
                for index in range(0, len(raw_results), 2)
            ]

        else:
            raise ValueError(
                "Redis returned an unsupported vector search result."
            )

        results = [
            VectorSearchResult(
                entry_id=str(entry_id),
                similarity_score=float(similarity_score),
            )
            for entry_id, similarity_score in scored_entries
        ]

        # Redis already ranks by descending similarity; sorting
        # keeps that guarantee independent of reply shape, since
        # the caller returns the first match above the threshold.
        results.sort(
            key=lambda result: result.similarity_score,
            reverse=True,
        )

        return results