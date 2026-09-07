from langchain_core.messages import BaseMessage, HumanMessage

from app.agent.agent_factory import create_workforce_agent
from app.agent.message_converter import (
    convert_conversation_history,
)
from app.agent.response_parser import parse_agent_result
from app.agent.tool_registry import create_agent_tools
from app.agent.types import AgentExecutionResult
from app.core.config import get_settings
from app.schemas.message import ConversationMessage


class AgentOrchestrator:
    """
    Coordinates tool loading, conversation-history conversion,
    agent creation, agent execution, and response parsing.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def run(
        self,
        *,
        question: str,
        context: str | None = None,
        conversation_history: (
            list[ConversationMessage] | None
        ) = None,
    ) -> AgentExecutionResult:
        """
        Execute the LangChain agent for one user question.

        Args:
            question:
                The current user question.

            context:
                Optional additional instructions or context
                supplied by the user.

            conversation_history:
                Previous user and assistant messages retrieved
                from Redis for the selected session.

        Returns:
            The final agent answer, tools used, source
            classification, and raw LangChain messages.
        """

        normalized_question = self._normalize_question(
            question
        )

        tools = await create_agent_tools()

        agent = create_workforce_agent(
            tools=tools
        )

        messages = self._build_messages(
            question=normalized_question,
            context=context,
            conversation_history=conversation_history,
        )

        recursion_limit = (
            self._settings.agent_max_iterations * 2
            + 2
        )

        result = await agent.ainvoke(
            {
                "messages": messages,
            },
            config={
                "recursion_limit": recursion_limit,
            },
        )

        if not isinstance(result, dict):
            raise ValueError(
                "Agent returned an unsupported result."
            )

        return parse_agent_result(result)

    def _build_messages(
        self,
        *,
        question: str,
        context: str | None,
        conversation_history: (
            list[ConversationMessage] | None
        ),
    ) -> list[BaseMessage]:
        """
        Build the LangChain message list from Redis history
        and the current user request.
        """

        messages: list[BaseMessage] = []

        if conversation_history:
            converted_history = (
                convert_conversation_history(
                    conversation_history
                )
            )

            messages.extend(converted_history)

        user_content = self._build_user_content(
            question=question,
            context=context,
        )

        messages.append(
            HumanMessage(
                content=user_content
            )
        )

        return messages

    @staticmethod
    def _normalize_question(
        question: str,
    ) -> str:
        """
        Trim and normalize whitespace in the user question.
        """

        normalized_question = " ".join(
            question.strip().split()
        )

        if not normalized_question:
            raise ValueError(
                "Question cannot be empty."
            )

        return normalized_question

    @staticmethod
    def _build_user_content(
        *,
        question: str,
        context: str | None,
    ) -> str:
        """
        Combine optional user context with the current question.
        """

        if context is None:
            return question

        normalized_context = context.strip()

        if not normalized_context:
            return question

        return (
            "Additional user context:\n"
            f"{normalized_context}\n\n"
            "Question:\n"
            f"{question}"
        )