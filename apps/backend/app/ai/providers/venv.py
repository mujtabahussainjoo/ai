"""Optional fully-local transformers provider (requires the 'rag-local' extra)."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from app.ai.base import AIProviderError, BaseLLMProvider, ModelCapability
from app.core.config import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer  # pragma: no cover

_LOCAL_IMPORT_ERROR = (
    "sentence-transformers is not installed. Enable the optional dependencies: "
    "cd apps/backend && .venv/bin/pip install -e '.[rag-local]'"
)

_encoder: SentenceTransformer | None = None


def _load_encoder(model: str) -> SentenceTransformer:
    global _encoder
    if _encoder is not None:
        return _encoder
    try:
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415
    except ImportError as exc:
        raise AIProviderError(
            _LOCAL_IMPORT_ERROR, provider="venv", code="optional_dependency_missing"
        ) from exc
    _encoder = SentenceTransformer(model)
    return _encoder


class LocalProvider(BaseLLMProvider):
    name = "venv"
    display_name = "Local transformers (venv)"
    capabilities = (ModelCapability.EMBEDDING, ModelCapability.CHAT)
    default_model = settings.DEFAULT_EMBEDDING_MODEL

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        encoder = await asyncio.to_thread(_load_encoder, model or self.effective_model)
        vectors = await asyncio.to_thread(encoder.encode, texts, normalize_embeddings=True)
        return [list(row) for row in vectors.tolist()]

    async def ping(self) -> bool:
        try:
            _load_encoder(self.effective_model)
            return True
        except AIProviderError:
            return False
