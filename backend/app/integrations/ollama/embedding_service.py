from app.integrations.ollama.client import OllamaClient


class EmbeddingService:
    def __init__(
        self,
        client: OllamaClient,
    ) -> None:
        self._client = client

    async def embed_text(
        self,
        text: str,
    ) -> list[float]:
        normalized_text = " ".join(
            text.strip().split()
        )

        if not normalized_text:
            raise ValueError(
                "Text cannot be empty."
            )

        return await self._client.generate_embedding(
            normalized_text
        )

    async def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        normalized_texts = [
            " ".join(text.strip().split())
            for text in texts
        ]

        if not normalized_texts:
            raise ValueError(
                "At least one text value is required."
            )

        if any(
            not text
            for text in normalized_texts
        ):
            raise ValueError(
                "Embedding texts cannot contain empty values."
            )

        return await self._client.generate_embeddings(
            normalized_texts
        )