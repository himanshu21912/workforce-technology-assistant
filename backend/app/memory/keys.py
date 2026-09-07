from app.core.config import get_settings


settings = get_settings()


def session_metadata_key(session_id: str) -> str:
    return (
        f"{settings.conversation_key_prefix}:"
        f"session:{session_id}"
    )


def session_history_key(session_id: str) -> str:
    return (
        f"{settings.conversation_key_prefix}:"
        f"history:{session_id}"
    )


def session_index_key() -> str:
    return (
        f"{settings.conversation_key_prefix}:sessions"
    )