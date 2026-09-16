"""Core abstractions for LLM providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class ModelCapability(StrEnum):
    CHAT = "chat"
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    TOOL_USE = "tool_use"


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    reasoning: str | None = None


class AIProviderError(Exception):
    """Provider-level failure mapped to a stable API error code."""

    def __init__(self, message: str, *, provider: str = "", code: str = "provider_error") -> None:
        self.provider = provider
        self.code = code
        super().__init__(message)


@dataclass
class ToolDefinition:
    """JSON-schema tool definition sent to tool-calling providers."""

    name: str
    description: str
    parameters: dict[str, Any]


class LLMProvider(Protocol):
    name: str
    display_name: str
    capabilities: tuple[str, ...]
    default_model: str

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse: ...

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]: ...

    async def ping(self) -> bool: ...


class BaseLLMProvider:
    name: str = ""
    display_name: str = ""
    capabilities: tuple[str, ...] = ()
    default_model: str = ""

    def __init__(
        self,
        *,
        api_key: str = "",
        base_url: str = "",
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model or self.default_model
        self.timeout = timeout

    async def chat(self, *args: Any, **kwargs: Any) -> LLMResponse:
        raise NotImplementedError

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        raise AIProviderError(f"{self.name} does not support embeddings", provider=self.name)

    async def ping(self) -> bool:
        return False

    @property
    def effective_model(self) -> str:
        return self.model
