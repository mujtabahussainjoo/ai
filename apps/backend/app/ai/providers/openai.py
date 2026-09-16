"""OpenAI provider via HTTPS chat-completions API."""

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

DEFAULT_BASE_URL = "https://api.openai.com/v1"


class OpenAIProvider(BaseLLMProvider):
    name = "openai"
    display_name = "OpenAI"
    capabilities = (
        ModelCapability.CHAT,
        ModelCapability.CODING,
        ModelCapability.VISION,
        ModelCapability.EMBEDDING,
        ModelCapability.TOOL_USE,
    )
    default_model = "gpt-4o-mini"

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
            "temperature": temperature if temperature is not None else 0.7,
            "max_tokens": max_tokens or 2048,
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
                    f"{self.base_url or DEFAULT_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise AIProviderError(f"openai request failed: {exc}", provider=self.name) from exc
        if response.status_code != 200:
            raise AIProviderError(
                f"openai returned {response.status_code}: {response.text[:300]}", provider=self.name
            )
        data = response.json()
        try:
            content = (data["choices"][0]["message"]["content"]) or ""
            tool_calls = data["choices"][0]["message"].get("tool_calls") or []
        except (KeyError, IndexError) as exc:
            raise AIProviderError(
                f"unexpected openai response shape: {str(data)[:300]}", provider=self.name
            ) from exc
        return LLMResponse(
            content=content,
            model=data.get("model", self.effective_model),
            provider=self.name,
            usage=data.get("usage") or {},
            tool_calls=tool_calls,
        )

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url or DEFAULT_BASE_URL}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": model or "text-embedding-3-small", "input": texts},
            )
        if response.status_code != 200:
            raise AIProviderError(f"openai embed returned {response.status_code}", provider=self.name)
        data = response.json()
        return [item["embedding"] for item in sorted(data["data"], key=lambda it: it["index"])]

    async def ping(self) -> bool:
        return bool(self.api_key and settings.OPENAI_API_KEY or self.api_key)
