from dataclasses import dataclass

from app.schemas.semantic_cache import SemanticCacheEntry


@dataclass(frozen=True)
class VectorSearchResult:
    entry_id: str
    similarity_score: float


@dataclass(frozen=True)
class CacheLookupResult:
    entry: SemanticCacheEntry
    similarity_score: float