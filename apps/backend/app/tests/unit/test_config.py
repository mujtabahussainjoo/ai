"""Unit tests for settings loading and derived values."""

from __future__ import annotations

from app.core.config import Settings


def test_defaults_are_safe() -> None:
    settings = Settings()
    assert settings.APP_ENV in {"development", "production"}
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.UPLOAD_DIR is not None


def test_database_url_derived() -> None:
    settings = Settings(
        POSTGRES_HOST="127.0.0.1",
        POSTGRES_PORT=5433,
        POSTGRES_USER="myaibuddy",
        POSTGRES_PASSWORD="myaibuddy_dev",
        POSTGRES_DB="myaibuddy",
    )
    assert settings.DATABASE_URL == "postgresql+asyncpg://myaibuddy:myaibuddy_dev@127.0.0.1:5433/myaibuddy"


def test_configured_providers() -> None:
    settings = Settings()
    assert isinstance(settings.configured_providers, list)
    assert settings.EMBEDDING_DIM >= 384
