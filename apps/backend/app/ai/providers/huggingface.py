"""Hugging Face provider for embeddings via the Inference API."""

from __future__ import annotations

import httpx

from app.ai.base import AIProviderError, BaseLLMProvider, LLMResponse, ModelCapability
from app.core.config import settings

DEFAULT_BASE_URL = "https://api-inference.huggingface.co"


class HuggingFaceProvider(BaseLLMProvider):
    name = "huggingface"
    display_name = "Hugging Face"
    capabilities = (ModelCapability.EMBEDDING,)
    default_model = settings.DEFAULT_EMBEDDING_MODEL

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        payload = {"inputs": texts, "options": {"wait_for_model": True}}
        try:
            async with httpx.AsyncClient(timeout=max(self.timeout, 90)) as client:
                response = await client.post(
                    f"{self.base_url or DEFAULT_BASE_URL}/pipeline/feature-extraction/{model or self.effective_model}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise AIProviderError(f"huggingface request failed: {exc}", provider=self.name) from exc
        if response.status_code != 200:
            raise AIProviderError(
                f"huggingface returned {response.status_code}: {response.text[:300]}", provider=self.name
            )
        data = response.json()
        if not data or not isinstance(data[0], list):
            raise AIProviderError(
                f"unexpected huggingface embedding shape: {str(data)[:200]}", provider=self.name
            )
        return [[float(value) for value in row] for row in data]

    async def chat(self, *args: object, **kwargs: object) -> LLMResponse:
        raise AIProviderError("huggingface chat not supported here", provider=self.name)

    async def ping(self) -> bool:
        return bool(self.api_key)
