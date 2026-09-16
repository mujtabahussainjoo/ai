"""Mock provider: deterministic local fallback for development, tests, and demos."""

from __future__ import annotations

import hashlib

from app.ai.base import BaseLLMProvider, ChatMessage, LLMResponse, ModelCapability, ToolDefinition


class MockLLMProvider(BaseLLMProvider):
    name = "mock"
    display_name = "Mock (offline)"
    capabilities = (ModelCapability.CHAT, ModelCapability.REASONING, ModelCapability.EMBEDDING)
    default_model = "mock-0.1"

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        last_user = ""
        for message in reversed(messages):
            if message.role == "user":
                last_user = message.content
                break
        digest = hashlib.sha256(last_user.encode()).hexdigest()[:6]
        reply = (
            f"[mock:{self.effective_model}] You wrote: “{last_user[:200]}”\n\n"
            "Running fully offline with the built-in mock provider. "
            f"(request sha-{digest}/^{hashlib.md5(self.effective_model.encode()).hexdigest()[:6]})\n\n"
            "To use a real model: configure a provider key (OpenAI/Anthropic) or start Ollama "
            "and enable it under Settings → Providers."
        )
        return LLMResponse(content=reply, model=self.effective_model, provider=self.name)

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        dim = 384
        vectors: list[list[float]] = []
        for text in texts:
            raw = hashlib.sha256(text.encode()).digest()
            expanded = list(raw) * ((dim // len(raw)) + 1)
            vectors.append([(byte / 255.0) - 0.5 for byte in expanded[:dim]])
        return vectors

    async def ping(self) -> bool:
        return True
