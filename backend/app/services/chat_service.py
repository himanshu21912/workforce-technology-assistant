from typing import TYPE_CHECKING

from app.core.config import get_settings
from app.core.exceptions import (
    AgentExecutionError,
    SessionNotFoundError,
)
from app.schemas.chat import AskResponse
from app.semantic_cache.cache_service import (
    SemanticCacheService,
)
from app.services.session_service import SessionService


if TYPE_CHECKING:
    from app.agent import AgentOrchestrator


class ChatService:
    """
    Coordinates session validation, conversation history,
    semantic-cache lookup, agent execution, and persistence.
    """

    def __init__(
        self,
        *,
        session_service: SessionService,
        semantic_cache_service: SemanticCacheService,
        agent_orchestrator: "AgentOrchestrator",
    ) -> None:
        self._session_service = session_service
        self._semantic_cache_service = (
            semantic_cache_service
        )
        self._agent_orchestrator = agent_orchestrator
        self._settings = get_settings()

    async def ask(
        self,
        *,
        session_id: str,
        question: str,
        context: str | None = None,
    ) -> AskResponse:
        normalized_question = self._normalize_question(
            question
        )

        session = await self._get_required_session(
            session_id
        )

        history = (
            await self._session_service.get_session_history(
                session_id=session_id
            )
        )

        cache_match = (
            await self._semantic_cache_service.lookup(
                session_id=session_id,
                question=normalized_question,
            )
        )

        if cache_match.cache_hit:
            if cache_match.entry is None:
                raise ValueError(
                    "Semantic cache reported a hit without "
                    "a cache entry."
                )

            await self._store_conversation_turn(
                session_id=session_id,
                question=normalized_question,
                answer=cache_match.entry.answer,
                source=cache_match.entry.source,
                tools_used=cache_match.entry.tools_used,
                cache_hit=True,
                similarity_score=(
                    cache_match.similarity_score
                ),
            )

            await self._update_default_session_title(
                session_id=session_id,
                current_title=session.title,
                question=normalized_question,
            )

            return AskResponse(
                session_id=session_id,
                answer=cache_match.entry.answer,
                cache_hit=True,
                similarity_score=(
                    cache_match.similarity_score
                ),
                source=cache_match.entry.source,
                tools_used=cache_match.entry.tools_used,
                model_name=cache_match.entry.model_name,
            )

        try:
            agent_result = await self._agent_orchestrator.run(
                question=normalized_question,
                context=context,
                conversation_history=history.messages,
            )
        except Exception as exception:
            raise AgentExecutionError(
                "The AI assistant could not complete "
                "the request."
            ) from exception

        await self._store_conversation_turn(
            session_id=session_id,
            question=normalized_question,
            answer=agent_result.answer,
            source=agent_result.source,
            tools_used=agent_result.tools_used,
            cache_hit=False,
            similarity_score=None,
        )

        try:
            await self._semantic_cache_service.store(
                session_id=session_id,
                question=normalized_question,
                answer=agent_result.answer,
                source=agent_result.source,
                tools_used=agent_result.tools_used,
                metadata={
                    "context": context,
                },
            )
        except Exception:
            # Cache storage failure must not discard an otherwise
            # successful answer.
            pass

        await self._update_default_session_title(
            session_id=session_id,
            current_title=session.title,
            question=normalized_question,
        )

        return AskResponse(
            session_id=session_id,
            answer=agent_result.answer,
            cache_hit=False,
            similarity_score=None,
            source=agent_result.source,
            tools_used=agent_result.tools_used,
            model_name=self._settings.ollama_chat_model,
        )

    async def clear_semantic_cache(
        self,
        session_id: str,
    ) -> int:
        return await (
            self._semantic_cache_service.clear_session(
                session_id
            )
        )

    async def _get_required_session(
        self,
        session_id: str,
    ):
        try:
            history = (
                await self._session_service
                .get_session_history(
                    session_id=session_id,
                    message_limit=1,
                )
            )

            return history.session

        except ValueError as exception:
            raise SessionNotFoundError(
                "The requested session was not found."
            ) from exception

    async def _store_conversation_turn(
        self,
        *,
        session_id: str,
        question: str,
        answer: str,
        source: str,
        tools_used: list[str],
        cache_hit: bool,
        similarity_score: float | None,
    ) -> None:
        await self._session_service.add_user_message(
            session_id=session_id,
            content=question,
            metadata={
                "message_type": "question",
            },
        )

        await self._session_service.add_assistant_message(
            session_id=session_id,
            content=answer,
            metadata={
                "source": source,
                "tools_used": tools_used,
                "cache_hit": cache_hit,
                "similarity_score": similarity_score,
            },
        )

    async def _update_default_session_title(
        self,
        *,
        session_id: str,
        current_title: str,
        question: str,
    ) -> None:
        if (
            current_title
            != self._settings.session_default_title
        ):
            return

        generated_title = question[:100].strip()

        if len(question) > 100:
            generated_title = (
                f"{generated_title.rstrip()}..."
            )

        await self._session_service.update_session_title(
            session_id=session_id,
            title=generated_title,
        )

    @staticmethod
    def _normalize_question(
        question: str,
    ) -> str:
        normalized = " ".join(
            question.strip().split()
        )

        if not normalized:
            raise ValueError(
                "Question cannot be empty."
            )

        return normalized
