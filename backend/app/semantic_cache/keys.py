from app.core.config import get_settings


settings = get_settings()


def semantic_vector_key(session_id: str) -> str:
    return (
        f"{settings.semantic_cache_key_prefix}:"
        f"vectors:{session_id}"
    )


def semantic_entry_key(
    session_id: str,
    entry_id: str,
) -> str:
    return (
        f"{settings.semantic_cache_key_prefix}:"
        f"entry:{session_id}:{entry_id}"
    )


def semantic_entry_index_key(
    session_id: str,
) -> str:
    return (
        f"{settings.semantic_cache_key_prefix}:"
        f"entries:{session_id}"
    )