"""Ollama provider for fully-local models (chat + embeddings)."""

from __future__ import annotations

import httpx

from app.ai.base import (
    AIProviderError,
    BaseLLMProvider,
    ChatMessage,
    LLMResponse,
    ModelCapability,
    ToolDefinition,
)
from app.core.config import settings


class OllamaProvider(BaseLLMProvider):
    name = "ollama"
    display_name = "Ollama (local)"
    capabilities = (
        ModelCapability.CHAT,
        ModelCapability.REASONING,
        ModelCapability.EMBEDDING,
        ModelCapability.TOOL_USE,
    )
    default_model = "llama3.2"

    def __init__(
        self,
        *,
        api_key: str = "",
        base_url: str = "",
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        super().__init__(
            api_key=api_key, base_url=base_url or settings.OLLAMA_BASE_URL, model=model, timeout=timeout
        )

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        payload: dict[str, object] = {
            "model": model or self.effective_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature if temperature is not None else 0.7},
        }
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {"name": t.name, "description": t.description, "parameters": t.parameters},
                }
                for t in tools
            ]
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/api/chat",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise AIProviderError(f"ollama request failed: {exc}", provider=self.name) from exc
        if response.status_code != 200:
            raise AIProviderError(
                f"ollama returned {response.status_code}: {response.text[:300]}", provider=self.name
            )
        data = response.json()
        message = data.get("message", {})
        return LLMResponse(
            content=message.get("content", ""),
            model=data.get("model", self.effective_model),
            provider=self.name,
            usage={
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0),
            },
        )

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        embeddings: list[list[float]] = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for text in texts:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/api/embed",
                    json={"model": model or "nomic-embed-text", "input": text},
                )
                if response.status_code != 200:
                    raise AIProviderError(f"ollama embed returned {response.status_code}", provider=self.name)
                data = response.json()
                embeddings.append(data["embeddings"][0])
        return embeddings

    async def ping(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url.rstrip('/')}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False
