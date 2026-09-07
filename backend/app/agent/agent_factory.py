from typing import Any

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from app.agent.prompts import SYSTEM_PROMPT
from app.core.config import get_settings
from app.integrations.llm import create_chat_model


def create_workforce_agent(
    tools: list[BaseTool],
) -> Any:
    """
    Create the LangChain agent using the configured Ollama
    chat model and all available tools.
    """

    settings = get_settings()
    model = create_chat_model()

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        debug=settings.agent_debug,
        name="workforce-technology-assistant",
    )

    return agent