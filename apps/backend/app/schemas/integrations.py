"""Third-party (external) API integration schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ThirdPartyApiOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    base_url: str | None = None
    method: str
    code: str | None
    key_fingerprint: str | None
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ThirdPartyApiCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=300)
    base_url: str | None = Field(default=None, max_length=500)
    method: str = Field(default="GET", pattern="^(GET|POST|PUT|PATCH|DELETE)$")
    code: str | None = None
    api_key: str | None = Field(default=None, max_length=2000)
    enabled: bool = True


class ThirdPartyApiUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=300)
    base_url: str | None = Field(default=None, min_length=1, max_length=500)
    method: str | None = Field(default=None, pattern="^(GET|POST|PUT|PATCH|DELETE)$")
    code: str | None = None
    api_key: str | None = Field(default=None, max_length=2000)
    enabled: bool | None = None
