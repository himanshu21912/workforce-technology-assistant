from langchain_ollama import ChatOllama

from app.core.config import get_settings


def create_chat_model() -> ChatOllama:
    """
    Create the configured local Ollama chat model.
    """

    settings = get_settings()

    return ChatOllama(
        model=settings.ollama_chat_model,
        base_url=settings.ollama_base_url,
        temperature=settings.ollama_temperature,
        num_ctx=settings.ollama_num_ctx,
    )