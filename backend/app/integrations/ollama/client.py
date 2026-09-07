from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import (
    OllamaEmbeddingError,
    OllamaUnavailableError,
)


class OllamaClient:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()

        self._owns_client = client is None

        self._client = client or httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=httpx.Timeout(
                settings.ollama_request_timeout
            ),
            follow_redirects=True,
        )

    async def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            raise ValueError(
                "At least one text value is required."
            )

        settings = get_settings()

        try:
            response = await self._client.post(
                "/api/embed",
                json={
                    "model": settings.ollama_embedding_model,
                    "input": texts,
                    "truncate": True,
                },
            )
        except httpx.TimeoutException as exception:
            raise OllamaUnavailableError(
                "The Ollama embedding request timed out."
            ) from exception
        except httpx.RequestError as exception:
            raise OllamaUnavailableError(
                "The Ollama service could not be reached."
            ) from exception

        if response.status_code >= 400:
            raise OllamaEmbeddingError(
                "Ollama failed to generate embeddings. "
                f"HTTP status: {response.status_code}."
            )

        try:
            response_data: Any = response.json()
        except ValueError as exception:
            raise OllamaEmbeddingError(
                "Ollama returned an invalid JSON response."
            ) from exception

        if not isinstance(response_data, dict):
            raise OllamaEmbeddingError(
                "Ollama returned an unsupported response."
            )

        embeddings = response_data.get("embeddings")

        if not isinstance(embeddings, list):
            raise OllamaEmbeddingError(
                "Ollama response does not contain embeddings."
            )

        if len(embeddings) != len(texts):
            raise OllamaEmbeddingError(
                "Ollama returned an unexpected embedding count."
            )

        validated_embeddings: list[list[float]] = []

        for embedding in embeddings:
            if not isinstance(embedding, list):
                raise OllamaEmbeddingError(
                    "Ollama returned an invalid embedding."
                )

            try:
                validated_embedding = [
                    float(value)
                    for value in embedding
                ]
            except (TypeError, ValueError) as exception:
                raise OllamaEmbeddingError(
                    "Ollama embedding contains invalid values."
                ) from exception

            if not validated_embedding:
                raise OllamaEmbeddingError(
                    "Ollama returned an empty embedding."
                )

            validated_embeddings.append(
                validated_embedding
            )

        return validated_embeddings

    async def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError(
                "Embedding text cannot be empty."
            )

        embeddings = await self.generate_embeddings(
            [normalized_text]
        )

        return embeddings[0]

    async def check_health(self) -> bool:
        try:
            response = await self._client.get(
                "/api/version"
            )

            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "OllamaClient":
        return self

    async def __aexit__(
        self,
        exception_type,
        exception,
        traceback,
    ) -> None:
        await self.close()