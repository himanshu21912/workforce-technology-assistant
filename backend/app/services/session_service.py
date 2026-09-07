from app.memory import (
    ConversationHistory,
    RedisHistoryRepository,
    SessionManager,
)
from app.schemas.message import ConversationMessage
from app.schemas.session import (
    ChatSession,
    SessionHistory,
)


class SessionService:
    def __init__(
        self,
        session_manager: SessionManager,
        conversation_history: ConversationHistory,
    ) -> None:
        self._session_manager = session_manager
        self._conversation_history = conversation_history

    @classmethod
    def from_repository(
        cls,
        repository: RedisHistoryRepository,
    ) -> "SessionService":
        return cls(
            session_manager=SessionManager(repository),
            conversation_history=ConversationHistory(
                repository
            ),
        )

    async def create_session(
        self,
        title: str | None = None,
    ) -> ChatSession:
        return await self._session_manager.create_session(
            title
        )

    async def list_sessions(
        self,
        limit: int | None = None,
    ) -> list[ChatSession]:
        return await self._session_manager.list_sessions(
            limit
        )

    async def get_session_history(
        self,
        session_id: str,
        message_limit: int | None = None,
    ) -> SessionHistory:
        session = await self._session_manager.require_session(
            session_id
        )

        messages = (
            await self._conversation_history.get_messages(
                session_id=session_id,
                limit=message_limit,
            )
        )

        refreshed_session = (
            await self._session_manager.require_session(
                session_id
            )
        )

        return SessionHistory(
            session=refreshed_session,
            messages=messages,
        )

    async def add_user_message(
        self,
        *,
        session_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        return (
            await self._conversation_history.add_user_message(
                session_id=session_id,
                content=content,
                metadata=metadata,
            )
        )

    async def add_assistant_message(
        self,
        *,
        session_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        return await (
            self._conversation_history.add_assistant_message(
                session_id=session_id,
                content=content,
                metadata=metadata,
            )
        )

    async def update_session_title(
        self,
        *,
        session_id: str,
        title: str,
    ) -> ChatSession:
        return await self._session_manager.update_title(
            session_id=session_id,
            title=title,
        )

    async def delete_session(
        self,
        session_id: str,
    ) -> bool:
        return await self._session_manager.delete_session(
            session_id
        )