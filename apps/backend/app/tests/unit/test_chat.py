"""Unit tests for the chat service system-prompt builder."""

from __future__ import annotations

import pytest

from app.ai.prompts import system_prompt


def test_system_prompt_includes_date() -> None:
    prompt = system_prompt("chat")
    assert "2026" in prompt
    assert "MyAIBuddy" in prompt


@pytest.mark.parametrize("kind", ["chat", "rag", "web_research", "all_rounder", "coding"])
def test_known_kinds_produce_nonempty_prompts(kind: str) -> None:
    prompt = system_prompt(kind)
    assert len(prompt) > 200
    assert "MyAIBuddy" in prompt


def test_document_context_appears_in_prompt() -> None:
    prompt = system_prompt("rag", document_context="The capital of France is Paris.")
    assert "France" in prompt
    assert "Document context" in prompt
