from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.config import get_settings
from app.memory.history_repository import (
    RedisHistoryRepository,
)
from app.schemas.session import ChatSession


class SessionManager:
    def __init__(
        self,
        repository: RedisHistoryRepository,
    ) -> None:
        self._repository = repository
        self._settings = get_settings()

    async def create_session(
        self,
        title: str | None = None,
    ) -> ChatSession:
        normalized_title = self._normalize_title(title)
        now = datetime.now(UTC)

        session = ChatSession(
            session_id=uuid4(),
            title=normalized_title,
            created_at=now,
            updated_at=now,
            message_count=0,
        )

        return await self._repository.create_session(
            session
        )

    async def get_session(
        self,
        session_id: str,
    ) -> ChatSession | None:
        self._validate_session_id(session_id)

        return await self._repository.get_session(
            session_id
        )

    async def require_session(
        self,
        session_id: str,
    ) -> ChatSession:
        session = await self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session '{session_id}' does not exist."
            )

        return session

    async def list_sessions(
        self,
        limit: int | None = None,
    ) -> list[ChatSession]:
        requested_limit = (
            limit
            if limit is not None
            else self._settings.session_list_limit
        )

        if requested_limit < 1:
            raise ValueError(
                "Session limit must be greater than zero."
            )

        return await self._repository.list_sessions(
            requested_limit
        )

    async def update_title(
        self,
        *,
        session_id: str,
        title: str,
    ) -> ChatSession:
        await self.require_session(session_id)

        normalized_title = self._normalize_title(title)

        await self._repository.update_session_title(
            session_id=session_id,
            title=normalized_title,
        )

        updated_session = await self.require_session(
            session_id
        )

        return updated_session

    async def delete_session(
        self,
        session_id: str,
    ) -> bool:
        self._validate_session_id(session_id)

        return await self._repository.delete_session(
            session_id
        )

    def _normalize_title(
        self,
        title: str | None,
    ) -> str:
        if title is None:
            return self._settings.session_default_title

        normalized_title = " ".join(
            title.strip().split()
        )

        if not normalized_title:
            return self._settings.session_default_title

        if len(normalized_title) > 150:
            raise ValueError(
                "Session title cannot exceed 150 characters."
            )

        return normalized_title

    @staticmethod
    def _validate_session_id(
        session_id: str,
    ) -> None:
        try:
            UUID(session_id)
        except (TypeError, ValueError) as exception:
            raise ValueError(
                "Session ID must be a valid UUID."
            ) from exception