"""Provider configuration and status endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import require_admin, require_user
from app.db.session import get_db
from app.schemas.common import envelope
from app.schemas.providers import ProviderPingRequest, ProviderTestResult, ProviderUpdateRequest
from app.services import providers as provider_service

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=dict[str, Any])
async def list_providers(
    _: Any = Depends(require_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    statuses = await provider_service.get_provider_statuses(db)
    return envelope([status.model_dump(mode="json") for status in statuses])


@router.put("/{provider}", response_model=dict[str, Any])
async def update_provider(
    provider: str,
    body: ProviderUpdateRequest,
    current_user: Any = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    status = await provider_service.upsert_provider(db, name=provider, body=body, actor_id=current_user.id)
    return envelope(status.model_dump(mode="json"))


@router.post("/{provider}/test", response_model=dict[str, Any])
async def test_provider(
    provider: str,
    body: ProviderPingRequest,
    current_user: Any = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    import httpx  # noqa: PLC0415

    from app.ai.registry import build_provider  # noqa: PLC0415

    api_key = body.api_key or ""
    base_url = body.base_url or ""
    instance = build_provider(provider, api_key=api_key, base_url=base_url, model=body.model)
    try:
        reachable = await instance.ping()
        detail = "reachable" if reachable else "not reachable or requires a valid key"
    except httpx.HTTPError as exc:
        reachable = False
        detail = str(exc)
    return envelope(
        ProviderTestResult(name=provider, reachable=reachable, detail=detail).model_dump(mode="json")
    )
