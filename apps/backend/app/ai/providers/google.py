"""Google Gemini provider via the v1beta REST API."""

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

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GoogleProvider(BaseLLMProvider):
    name = "google"
    display_name = "Google (Gemini)"
    capabilities = (
        ModelCapability.CHAT,
        ModelCapability.REASONING,
        ModelCapability.VISION,
        ModelCapability.EMBEDDING,
        ModelCapability.TOOL_USE,
    )
    default_model = "gemini-1.5-flash"

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        content: list[dict[str, object]] = []
        for message in messages:
            if message.role in {"user", "model"}:
                content.append(
                    {
                        "role": "model" if message.role == "assistant" else message.role,
                        "parts": [{"text": message.content}],
                    }
                )
        payload: dict[str, object] = {"contents": content}
        if tools:
            payload["tools"] = [
                {
                    "functionDeclarations": [
                        {"name": t.name, "description": t.description, "parameters": t.parameters}
                        for t in tools
                    ]
                }
            ]
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url or DEFAULT_BASE_URL}/models/{model or self.effective_model}:generateContent",
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise AIProviderError(f"google request failed: {exc}", provider=self.name) from exc
        if response.status_code != 200:
            raise AIProviderError(
                f"google returned {response.status_code}: {response.text[:300]}", provider=self.name
            )
        data = response.json()
        try:
            text = "".join(
                part.get("text", "")
                for candidate in data.get("candidates", [])
                for part in candidate.get("content", {}).get("parts", [])
            )
        except TypeError:
            text = ""
        return LLMResponse(content=text, model=self.effective_model, provider=self.name)

    async def ping(self) -> bool:
        return bool(self.api_key)
