"""Third-party API integration endpoints (admin-managed)."""

from __future__ import annotations

import uuid as _uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import require_admin, require_user
from app.db.session import get_db
from app.schemas.common import envelope
from app.schemas.integrations import (
    ThirdPartyApiCreate,
    ThirdPartyApiUpdate,
)
from app.services import integrations as integration_service

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=dict[str, Any])
async def list_integrations(
    _: Any = Depends(require_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    items = await integration_service.list_integrations(db)
    return envelope([item.model_dump(mode="json") for item in items])


@router.post("", response_model=dict[str, Any])
async def create_integration(
    body: ThirdPartyApiCreate,
    current_user: Any = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    item = await integration_service.create_integration(db, body=body, actor_id=current_user.id)
    return envelope(item.model_dump(mode="json"))


@router.put("/{integration_id}", response_model=dict[str, Any])
async def update_integration(
    integration_id: _uuid.UUID,
    body: ThirdPartyApiUpdate,
    current_user: Any = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    item = await integration_service.update_integration(
        db, integration_id=integration_id, body=body, actor_id=current_user.id
    )
    return envelope(item.model_dump(mode="json"))


@router.delete("/{integration_id}", response_model=dict[str, Any])
async def delete_integration(
    integration_id: _uuid.UUID,
    current_user: Any = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await integration_service.delete_integration(
        db, integration_id=integration_id, actor_id=current_user.id
    )
    return envelope({"status": "ok"})
