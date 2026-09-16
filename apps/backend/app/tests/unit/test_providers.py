"""Unit tests for the provider registry, mock provider, and secret encryption."""

from __future__ import annotations

import asyncio

import pytest

from app.ai.base import AIProviderError, ChatMessage
from app.ai.encryption import decrypt_secret, encrypt_secret, fingerprint
from app.ai.registry import build_provider, list_provider_names
from app.services.providers import _is_usable_for_chat, _skip_reason


def test_provider_registry_has_expected_backends() -> None:
    names = set(list_provider_names())
    assert {"mock", "openai", "anthropic", "ollama", "google", "venv"}.issubset(names)


def test_build_provider_unknown() -> None:
    with pytest.raises(AIProviderError):
        build_provider("does-not-exist")


def test_secret_encryption_roundtrip() -> None:
    blob = encrypt_secret("sk-secret-123")
    assert blob != b"sk-secret-123"
    assert decrypt_secret(blob) == "sk-secret-123"
    assert fingerprint("sk-secret-123") == fingerprint("sk-secret-123")


def test_mock_chat_returns_echo() -> None:
    async def run() -> str:
        provider = build_provider("mock")
        response = await provider.chat([ChatMessage(role="user", content="hello world")])
        return response.content

    content = asyncio.run(run())
    assert "hello world" in content


def test_mock_embeddings_shape() -> None:
    async def run() -> list[list[float]]:
        provider = build_provider("mock")
        return await provider.embed(["alpha", "beta beta"])

    vectors = asyncio.run(run())
    assert len(vectors) == 2
    assert len(vectors[0]) == 384


def test_is_usable_for_chat_mock_always_true() -> None:
    assert _is_usable_for_chat("mock", api_key="", base_url="") is True


def test_is_usable_for_chat_apikey_provider_requires_key() -> None:
    assert _is_usable_for_chat("openai", api_key="", base_url="") is False
    assert _is_usable_for_chat("openai", api_key="sk-test", base_url="") is True


def test_is_usable_for_chat_hf_no_chat_capability() -> None:
    assert _is_usable_for_chat("huggingface", api_key="hf_token", base_url="") is False
    assert _skip_reason("huggingface", api_key="hf_token", base_url="") == (
        "Hugging Face does not support chat in this build"
    )


def test_skip_reason_openai_missing_key() -> None:
    assert _skip_reason("openai", api_key="", base_url="") == (
        "OpenAI is enabled but no API key is configured"
    )
