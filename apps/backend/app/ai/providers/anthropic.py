"""Anthropic provider via the Messages API."""

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

DEFAULT_BASE_URL = "https://api.anthropic.com/v1"


class AnthropicProvider(BaseLLMProvider):
    name = "anthropic"
    display_name = "Anthropic"
    capabilities = (
        ModelCapability.CHAT,
        ModelCapability.REASONING,
        ModelCapability.CODING,
        ModelCapability.VISION,
        ModelCapability.TOOL_USE,
    )
    default_model = "claude-3-5-haiku-latest"

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        system_text = " ".join(m.content for m in messages if m.role == "system")
        payload: dict[str, object] = {
            "model": model or self.effective_model,
            "messages": [
                {"role": m.role, "content": m.content} for m in messages if m.role in {"user", "assistant"}
            ],
            "max_tokens": max_tokens or 2048,
            "temperature": temperature if temperature is not None else 0.7,
        }
        if tools:
            payload["tools"] = [
                {"name": t.name, "description": t.description, "input_schema": t.parameters} for t in tools
            ]
        if system_text:
            payload["system"] = system_text
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url or DEFAULT_BASE_URL}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise AIProviderError(f"anthropic request failed: {exc}", provider=self.name) from exc
        if response.status_code != 200:
            raise AIProviderError(
                f"anthropic returned {response.status_code}: {response.text[:300]}", provider=self.name
            )
        data = response.json()
        text = "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        )
        tool_calls = [
            block.get("input", {}) for block in data.get("content", []) if block.get("type") == "tool_use"
        ]
        return LLMResponse(
            content=text,
            model=data.get("model", self.effective_model),
            provider=self.name,
            usage={
                "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
            },
            tool_calls=tool_calls,
        )

    async def ping(self) -> bool:
        return bool(self.api_key)
