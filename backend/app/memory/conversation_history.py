from app.core.config import get_settings
from app.memory.history_repository import (
    RedisHistoryRepository,
)
from app.memory.message_window import apply_message_window
from app.schemas.message import (
    ConversationMessage,
    MessageRole,
)


class ConversationHistory:
    def __init__(
        self,
        repository: RedisHistoryRepository,
    ) -> None:
        self._repository = repository
        self._settings = get_settings()

    async def add_message(
        self,
        *,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        exists = await self._repository.session_exists(
            session_id
        )

        if not exists:
            raise ValueError(
                f"Session '{session_id}' does not exist."
            )

        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        await self._repository.append_message(
            session_id=session_id,
            message=message,
        )

        return message

    async def add_user_message(
        self,
        *,
        session_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        return await self.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=content,
            metadata=metadata,
        )

    async def add_assistant_message(
        self,
        *,
        session_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        return await self.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=content,
            metadata=metadata,
        )

    async def get_messages(
        self,
        *,
        session_id: str,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        exists = await self._repository.session_exists(
            session_id
        )

        if not exists:
            raise ValueError(
                f"Session '{session_id}' does not exist."
            )

        requested_limit = (
            limit
            if limit is not None
            else self._settings.conversation_max_messages
        )

        messages = await self._repository.get_messages(
            session_id=session_id,
            limit=requested_limit,
        )

        await self._repository.refresh_session_ttl(
            session_id
        )

        return apply_message_window(
            messages,
            requested_limit,
        )