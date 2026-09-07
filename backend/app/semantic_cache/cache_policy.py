from app.core.config import get_settings


class SemanticCachePolicy:
    FRESHNESS_KEYWORDS = {
        "current",
        "currently",
        "latest",
        "live",
        "now",
        "newest",
        "recent",
        "recently",
        "refresh",
        "refreshed",
        "today",
        "updated",
    }

    NON_CACHEABLE_SOURCES = {
        "error",
        "validation_error",
        "system_error",
    }

    def __init__(self) -> None:
        self._settings = get_settings()

    def should_bypass_lookup(
        self,
        question: str,
    ) -> bool:
        if not self._settings.semantic_cache_enabled:
            return True

        normalized_words = {
            word.strip(".,?!:;()[]{}\"'").lower()
            for word in question.split()
        }

        return bool(
            normalized_words
            & self.FRESHNESS_KEYWORDS
        )

    def should_store_response(
        self,
        *,
        question: str,
        answer: str,
        source: str,
    ) -> bool:
        if not self._settings.semantic_cache_enabled:
            return False

        if not question.strip() or not answer.strip():
            return False

        if source in self.NON_CACHEABLE_SOURCES:
            return False

        return True

    def is_similarity_match(
        self,
        similarity_score: float,
    ) -> bool:
        return (
            similarity_score
            >= self._settings.semantic_cache_similarity_threshold
        )