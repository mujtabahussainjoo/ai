"""Admin-only endpoints for inspecting backend activity, e.g. recent logs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps.auth import require_admin
from app.core.logging import recent_logs
from app.schemas.common import envelope

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/logs", response_model=dict[str, Any])
async def list_recent_logs(
    _: Any = Depends(require_admin),
    min_level: str = Query("WARNING", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    limit: int = Query(100, ge=1, le=400),
) -> dict[str, Any]:
    """Return the most recent buffered log records (admin only)."""
    entries = recent_logs(min_level=min_level, limit=limit)
    return envelope(entries)
