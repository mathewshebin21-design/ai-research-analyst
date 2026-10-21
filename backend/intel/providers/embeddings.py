"""Optional dense embeddings. Retrieval works without them (BM25); with a key, scores blend both."""

from typing import Protocol

from intel.providers.errors import ProviderError
from intel.providers.usage import Usage


class Embedder(Protocol):
    def embed(self, texts: list[str], usage: Usage) -> list[list[float]]: ...


class GeminiEmbedder:
    def __init__(self, api_key: str, model: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self.model = model

    def embed(self, texts: list[str], usage: Usage) -> list[list[float]]:
        out: list[list[float]] = []
        try:
            for i in range(0, len(texts), 64):
                batch = texts[i : i + 64]
                result = self._client.models.embed_content(model=self.model, contents=batch)
                usage.embedding_calls += 1
                out.extend([list(e.values or []) for e in result.embeddings or []])
        except Exception as exc:  # noqa: BLE001 - surface any SDK failure as a provider error
            raise ProviderError("Embedding request failed.") from exc
        if len(out) != len(texts):
            raise ProviderError("Embedding response was incomplete.")
        return out
