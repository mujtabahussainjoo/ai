"""Runtime configuration models: app settings and encrypted provider credentials."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class AppSetting(Base):
    """Non-secret dynamic settings (key/value JSON)."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    group: Mapped[str | None] = mapped_column(String(60))
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ProviderCredential(Base, IdMixin, TimestampMixin):
    __tablename__ = "provider_credentials"

    provider: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    encrypted_api_key: Mapped[bytes | None] = mapped_column(BYTEA)
    key_fingerprint: Mapped[str | None] = mapped_column(String(64))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    model_chat: Mapped[str | None] = mapped_column(String(120))
    model_reasoning: Mapped[str | None] = mapped_column(String(120))
    model_embedding: Mapped[str | None] = mapped_column(String(120))
    model_image: Mapped[str | None] = mapped_column(String(120))
    base_url: Mapped[str | None] = mapped_column(String(300))
    fallback_order: Mapped[int | None] = mapped_column(Integer)
    capabilities: Mapped[list[str] | None] = mapped_column(JSONB)


class ThirdPartyApi(Base, IdMixin, TimestampMixin):
    """User-defined 3rd-party API endpoints with stored credentials."""

    __tablename__ = "third_party_apis"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(300))
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(12), nullable=False, default="GET")
    code: Mapped[str | None] = mapped_column(Text)
    auth_type: Mapped[str] = mapped_column(String(30), nullable=False, default="bearer")
    header_name: Mapped[str | None] = mapped_column(String(120))
    encrypted_key: Mapped[bytes | None] = mapped_column(BYTEA)
    key_fingerprint: Mapped[str | None] = mapped_column(String(64))
    extra_headers: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
