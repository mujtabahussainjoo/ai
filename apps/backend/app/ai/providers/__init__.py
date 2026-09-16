"""Provider implementations."""

from app.ai.base import BaseLLMProvider
from app.ai.providers.anthropic import AnthropicProvider
from app.ai.providers.google import GoogleProvider
from app.ai.providers.huggingface import HuggingFaceProvider
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.ollama import OllamaProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.venv import LocalProvider

__all__ = [
    "AnthropicProvider",
    "GoogleProvider",
    "HuggingFaceProvider",
    "LocalProvider",
    "MockLLMProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "BaseLLMProvider",
]

PROVIDER_CLASSES: dict[str, type[BaseLLMProvider]] = {
    cls.name: cls
    for cls in (
        MockLLMProvider,
        OpenAIProvider,
        AnthropicProvider,
        GoogleProvider,
        HuggingFaceProvider,
        OllamaProvider,
        LocalProvider,
    )
}
