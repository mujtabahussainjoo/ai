"""Provider registry and factory."""

from __future__ import annotations

from app.ai.base import AIProviderError, BaseLLMProvider
from app.ai.providers import PROVIDER_CLASSES
from app.core.config import settings


def list_provider_names() -> list[str]:
    return list(PROVIDER_CLASSES)


def build_provider(
    name: str,
    *,
    api_key: str = "",
    base_url: str = "",
    model: str | None = None,
    timeout: float | None = None,
) -> BaseLLMProvider:
    provider_cls = PROVIDER_CLASSES.get(name)
    if provider_cls is None:
        raise AIProviderError(f"Unknown provider: {name}", code="unknown_provider")
    return provider_cls(
        api_key=api_key,
        base_url=base_url,
        model=model,
        timeout=timeout if timeout is not None else settings.LLM_TIMEOUT_SECONDS,
    )


def provider_meta(name: str) -> tuple[str, tuple[str, ...], str]:
    """Return (display_name, capabilities, default_model) for a provider."""
    provider_cls = PROVIDER_CLASSES.get(name)
    if provider_cls is None:
        raise AIProviderError(f"Unknown provider: {name}", code="unknown_provider")
    return provider_cls.display_name, provider_cls.capabilities, provider_cls.default_model


_PROVIDER_GUIDANCE: dict[str, dict[str, list[str]]] = {
    "mock": {
        "chat": ["mock-0.1"],
        "reasoning": ["mock-0.1"],
        "embedding": ["mock-0.1"],
    },
    "openai": {
        "chat": ["gpt-4o-mini", "gpt-4o"],
        "reasoning": ["gpt-4o"],
        "embedding": ["text-embedding-3-small", "text-embedding-3-large"],
    },
    "anthropic": {
        "chat": ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"],
        "reasoning": ["claude-3-5-sonnet-latest"],
        "embedding": ["voyage-ai/large-instruct (via Voyage)"],
    },
    "google": {
        "chat": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "reasoning": ["gemini-1.5-pro"],
        "embedding": ["text-embedding-004"],
    },
    "huggingface": {
        "embedding": ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5"],
    },
    "ollama": {
        "chat": ["llama3.2", "qwen2.5", "mistral"],
        "reasoning": ["qwen2.5"],
        "embedding": ["nomic-embed-text", "mxbai-embed-large"],
    },
    "venv": {
        "chat": ["meta-llama/Llama-3.2-1B-Instruct (via HF transformers)"],
        "embedding": ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5"],
    },
}

_RESOURCE_KEY: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "huggingface": "HUGGINGFACE_API_TOKEN",
}

_CHAT_UNSUPPORTED: set[str] = {"huggingface"}


def provider_meta_with_guidance(name: str) -> tuple[str, tuple[str, ...], str, dict[str, list[str]], str]:
    """Return (display_name, capabilities, default_model, model_suggestions, notes)."""
    display_name, capabilities, default_model = provider_meta(name)
    suggestions = _PROVIDER_GUIDANCE.get(name, {})
    notes = ""
    if name in _RESOURCE_KEY:
        notes = f"Requires {_RESOURCE_KEY[name]} (an API key) to work."
    if name == "mock":
        notes = "Offline mock. Works with no key and no network."
    if name == "ollama":
        notes = "Local Ollama server. No API key required, but Ollama must be running."
    if name == "venv":
        notes = "Runs Hugging Face transformers in-process. Slow on CPU; use for local/RAG embeddings."
    if name in _CHAT_UNSUPPORTED:
        notes = "Chat is NOT supported by this provider in this build. Use it only for embeddings."
    if name == "google":
        notes = "Requires GOOGLE_API_KEY (Gemini). Embeddings need a separate embedding API key."
    if name == "anthropic":
        notes = "Requires ANTHROPIC_API_KEY. Embeddings are not provided by Anthropic itself."
    return display_name, capabilities, default_model, suggestions, notes
