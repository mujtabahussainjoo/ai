"""Health and readiness endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, object]:
    return {
        "data": {
            "status": "ok",
            "version": settings.VERSION,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        "error": None,
    }


@router.get("/ready", summary="Readiness probe (checks database)")
async def ready(db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    database = "down"
    try:
        await db.execute(text("SELECT 1"))
        database = "up"
    except Exception:  # noqa: BLE001 - readiness must not fail the probe itself
        pass
    return {
        "data": {
            "status": "ok" if database == "up" else "degraded",
            "database": database,
            "version": settings.VERSION,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        "error": None,
    }
