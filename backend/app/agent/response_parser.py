from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ToolMessage,
)

from app.agent.tool_registry import (
    determine_agent_source,
)
from app.agent.types import AgentExecutionResult


def extract_text_content(
    content: Any,
) -> str:
    """
    Extract readable text from a LangChain message content value.
    """

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts: list[str] = []

        for block in content:
            if isinstance(block, str):
                normalized_block = block.strip()

                if normalized_block:
                    text_parts.append(
                        normalized_block
                    )

                continue

            if not isinstance(block, dict):
                continue

            block_type = block.get("type")

            if block_type not in {
                "text",
                "output_text",
            }:
                continue

            text = block.get("text")

            if isinstance(text, str):
                normalized_text = text.strip()

                if normalized_text:
                    text_parts.append(
                        normalized_text
                    )

        return "\n".join(text_parts)

    if content is None:
        return ""

    return str(content).strip()


def extract_tools_used(
    messages: list[BaseMessage],
) -> list[str]:
    """
    Extract unique tool names from AI tool calls and tool-result
    messages while preserving execution order.
    """

    tools_used: list[str] = []

    for message in messages:
        if isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                tool_name = tool_call.get("name")

                if (
                    isinstance(tool_name, str)
                    and tool_name.strip()
                    and tool_name not in tools_used
                ):
                    tools_used.append(tool_name)

        if isinstance(message, ToolMessage):
            tool_name = getattr(
                message,
                "name",
                None,
            )

            if (
                isinstance(tool_name, str)
                and tool_name.strip()
                and tool_name not in tools_used
            ):
                tools_used.append(tool_name)

    return tools_used


def parse_agent_result(
    result: dict[str, Any],
) -> AgentExecutionResult:
    """
    Parse the final answer and tool usage from a LangChain agent
    result.
    """

    raw_messages = result.get("messages")

    if not isinstance(raw_messages, list):
        raise ValueError(
            "Agent result does not contain a valid message list."
        )

    final_answer = ""

    for message in reversed(raw_messages):
        if not isinstance(message, AIMessage):
            continue

        if message.tool_calls:
            continue

        candidate_answer = extract_text_content(
            message.content
        )

        if candidate_answer:
            final_answer = candidate_answer
            break

    if not final_answer:
        raise ValueError(
            "Agent did not produce a final answer."
        )

    typed_messages = [
        message
        for message in raw_messages
        if isinstance(message, BaseMessage)
    ]

    tools_used = extract_tools_used(
        typed_messages
    )

    source = determine_agent_source(
        tools_used
    )

    return AgentExecutionResult(
        answer=final_answer,
        tools_used=tools_used,
        source=source,
        raw_messages=raw_messages,
    )