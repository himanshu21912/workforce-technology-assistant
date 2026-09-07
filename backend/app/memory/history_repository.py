from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis

from app.core.config import get_settings
from app.memory.keys import (
    session_history_key,
    session_index_key,
    session_metadata_key,
)
from app.schemas.message import ConversationMessage
from app.schemas.session import ChatSession


class RedisHistoryRepository:
    def __init__(self, client: Redis) -> None:
        self._client = client
        self._settings = get_settings()

    async def create_session(
        self,
        session: ChatSession,
    ) -> ChatSession:
        session_id = str(session.session_id)
        metadata_key = session_metadata_key(session_id)

        metadata = {
            "session_id": session_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": str(session.message_count),
        }

        updated_timestamp = session.updated_at.timestamp()

        async with self._client.pipeline(
            transaction=True,
        ) as pipeline:
            pipeline.hset(
                metadata_key,
                mapping=metadata,
            )
            pipeline.expire(
                metadata_key,
                self._settings.conversation_ttl_seconds,
            )
            pipeline.zadd(
                session_index_key(),
                {
                    session_id: updated_timestamp,
                },
            )

            await pipeline.execute()

        return session

    async def session_exists(
        self,
        session_id: str,
    ) -> bool:
        return bool(
            await self._client.exists(
                session_metadata_key(session_id)
            )
        )

    async def get_session(
        self,
        session_id: str,
    ) -> ChatSession | None:
        metadata = await self._client.hgetall(
            session_metadata_key(session_id)
        )

        if not metadata:
            return None

        return self._deserialize_session(metadata)

    async def list_sessions(
        self,
        limit: int,
    ) -> list[ChatSession]:
        session_ids = await self._client.zrevrange(
            session_index_key(),
            0,
            limit - 1,
        )

        sessions: list[ChatSession] = []
        stale_session_ids: list[str] = []

        for session_id in session_ids:
            session = await self.get_session(session_id)

            if session is None:
                stale_session_ids.append(session_id)
                continue

            sessions.append(session)

        if stale_session_ids:
            await self._client.zrem(
                session_index_key(),
                *stale_session_ids,
            )

        return sessions

    async def append_message(
        self,
        session_id: str,
        message: ConversationMessage,
    ) -> None:
        metadata_key = session_metadata_key(session_id)
        history_key = session_history_key(session_id)
        now = datetime.now(UTC)

        serialized_message = message.model_dump_json()

        async with self._client.pipeline(
            transaction=True,
        ) as pipeline:
            pipeline.rpush(
                history_key,
                serialized_message,
            )
            pipeline.ltrim(
                history_key,
                -self._settings.conversation_max_messages,
                -1,
            )
            pipeline.expire(
                history_key,
                self._settings.conversation_ttl_seconds,
            )
            pipeline.hincrby(
                metadata_key,
                "message_count",
                1,
            )
            pipeline.hset(
                metadata_key,
                mapping={
                    "updated_at": now.isoformat(),
                },
            )
            pipeline.expire(
                metadata_key,
                self._settings.conversation_ttl_seconds,
            )
            pipeline.zadd(
                session_index_key(),
                {
                    session_id: now.timestamp(),
                },
            )

            await pipeline.execute()

    async def get_messages(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        history_key = session_history_key(session_id)

        if limit is None:
            start = 0
        else:
            if limit < 1:
                raise ValueError(
                    "Message limit must be greater than zero."
                )

            start = -limit

        serialized_messages = await self._client.lrange(
            history_key,
            start,
            -1,
        )

        messages: list[ConversationMessage] = []

        for serialized_message in serialized_messages:
            messages.append(
                ConversationMessage.model_validate_json(
                    serialized_message
                )
            )

        return messages

    async def refresh_session_ttl(
        self,
        session_id: str,
    ) -> None:
        metadata_key = session_metadata_key(session_id)
        history_key = session_history_key(session_id)

        async with self._client.pipeline(
            transaction=True,
        ) as pipeline:
            pipeline.expire(
                metadata_key,
                self._settings.conversation_ttl_seconds,
            )
            pipeline.expire(
                history_key,
                self._settings.conversation_ttl_seconds,
            )

            await pipeline.execute()

    async def update_session_title(
        self,
        session_id: str,
        title: str,
    ) -> None:
        metadata_key = session_metadata_key(session_id)
        now = datetime.now(UTC)

        async with self._client.pipeline(
            transaction=True,
        ) as pipeline:
            pipeline.hset(
                metadata_key,
                mapping={
                    "title": title,
                    "updated_at": now.isoformat(),
                },
            )
            pipeline.expire(
                metadata_key,
                self._settings.conversation_ttl_seconds,
            )
            pipeline.zadd(
                session_index_key(),
                {
                    session_id: now.timestamp(),
                },
            )

            await pipeline.execute()

    async def delete_session(
        self,
        session_id: str,
    ) -> bool:
        metadata_key = session_metadata_key(session_id)
        history_key = session_history_key(session_id)

        async with self._client.pipeline(
            transaction=True,
        ) as pipeline:
            pipeline.delete(
                metadata_key,
                history_key,
            )
            pipeline.zrem(
                session_index_key(),
                session_id,
            )

            results = await pipeline.execute()

        deleted_key_count = int(results[0])

        return deleted_key_count > 0

    @staticmethod
    def _deserialize_session(
        metadata: dict[str, str],
    ) -> ChatSession:
        return ChatSession(
            session_id=UUID(metadata["session_id"]),
            title=metadata["title"],
            created_at=datetime.fromisoformat(
                metadata["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                metadata["updated_at"]
            ),
            message_count=int(
                metadata.get("message_count", "0")
            ),
        )