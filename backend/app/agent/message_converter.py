from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.schemas.message import (
    ConversationMessage,
    MessageRole,
)


def convert_conversation_message(
    message: ConversationMessage,
) -> BaseMessage | None:
    """
    Convert one stored Redis conversation message into a
    LangChain message.
    """

    message_id = str(message.id)

    if message.role == MessageRole.USER:
        return HumanMessage(
            content=message.content,
            id=message_id,
        )

    if message.role == MessageRole.ASSISTANT:
        return AIMessage(
            content=message.content,
            id=message_id,
        )

    if message.role == MessageRole.SYSTEM:
        return SystemMessage(
            content=message.content,
            id=message_id,
        )

    if message.role == MessageRole.TOOL:
        tool_call_id = message.metadata.get(
            "tool_call_id"
        )

        tool_name = message.metadata.get(
            "tool_name"
        )

        if not isinstance(tool_call_id, str):
            return None

        if not tool_call_id.strip():
            return None

        return ToolMessage(
            content=message.content,
            tool_call_id=tool_call_id,
            name=(
                tool_name
                if isinstance(tool_name, str)
                else None
            ),
            id=message_id,
        )

    return None


def convert_conversation_history(
    messages: list[ConversationMessage],
) -> list[BaseMessage]:
    """
    Convert Redis conversation history into LangChain messages.

    Unsupported or malformed messages are skipped.
    """

    converted_messages: list[BaseMessage] = []

    for message in messages:
        converted_message = (
            convert_conversation_message(message)
        )

        if converted_message is not None:
            converted_messages.append(
                converted_message
            )

    return converted_messages