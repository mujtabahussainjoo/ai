"""Provider status and update schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderStatus(BaseModel):
    name: str
    display_name: str
    description: str = ""
    model_suggestions: dict[str, list[str]] = Field(default_factory=dict)
    chat_unsupported: bool = False
    enabled: bool
    configured: bool
    key_fingerprint: str | None
    default_model: str
    model_chat: str | None
    model_reasoning: str | None
    model_embedding: str | None
    model_image: str | None
    base_url: str | None
    fallback_order: int | None
    capabilities: list[str]
    is_default: bool = False


class ProviderUpdateRequest(BaseModel):
    api_key: str | None = Field(default=None, min_length=8)
    base_url: str | None = Field(default=None, max_length=300)
    enabled: bool | None = None
    set_default: bool | None = None
    model_chat: str | None = Field(default=None, max_length=120)
    model_reasoning: str | None = Field(default=None, max_length=120)
    model_embedding: str | None = Field(default=None, max_length=120)
    model_image: str | None = Field(default=None, max_length=120)
    fallback_order: int | None = Field(default=None, ge=0, le=100)


class ProviderTestResult(BaseModel):
    name: str
    reachable: bool
    detail: str


class ResolvedProvider(BaseModel):
    name: str
    model: str
    source: str  # db | env | default


class ProviderPingRequest(BaseModel):
    api_key: str | None = Field(default=None, min_length=8)
    base_url: str | None = None
    model: str | None = None
