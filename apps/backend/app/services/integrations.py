"""Third-party API integration service: encrypted CRUD."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.encryption import decrypt_secret, encrypt_secret, fingerprint
from app.core.exceptions import ValidationError
from app.db.models import ThirdPartyApi
from app.schemas.integrations import (
    ThirdPartyApiCreate,
    ThirdPartyApiOut,
    ThirdPartyApiUpdate,
)
from app.services.audit import record_audit


def _to_out(row: ThirdPartyApi) -> ThirdPartyApiOut:
    return ThirdPartyApiOut(
        id=row.id,
        name=row.name,
        description=row.description,
        base_url=row.base_url,
        method=getattr(row, "method", "GET"),
        code=getattr(row, "code", None),
        key_fingerprint=row.key_fingerprint,
        enabled=row.enabled,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def list_integrations(session: AsyncSession) -> list[ThirdPartyApiOut]:
    rows = (
        (await session.execute(select(ThirdPartyApi).order_by(ThirdPartyApi.name.asc())))
        .scalars()
        .all()
    )
    return [_to_out(row) for row in rows]


async def create_integration(
    session: AsyncSession,
    *,
    body: ThirdPartyApiCreate,
    actor_id: uuid.UUID,
) -> ThirdPartyApiOut:
    existing = (
        await session.execute(
            select(ThirdPartyApi).where(ThirdPartyApi.name == body.name.strip())
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise ValidationError(f"An API integration named '{body.name}' already exists")

    cleaned_base_url = body.base_url.strip() if body.base_url else None
    row = ThirdPartyApi(
        name=body.name.strip(),
        description=body.description,
        base_url=cleaned_base_url,
        method=body.method,
        code=body.code,
        auth_type="bearer",
        encrypted_key=None,
        enabled=body.enabled,
        owner_id=actor_id,
    )
    if body.api_key:
        row.encrypted_key = encrypt_secret(body.api_key)
        row.key_fingerprint = fingerprint(body.api_key)
    session.add(row)
    await record_audit(
        session,
        action="settings.integration_created",
        actor_id=actor_id,
        resource_type="third_party_api",
        resource_id=str(row.id),
        details={"name": row.name, "base_url": row.base_url, "enabled": row.enabled},
    )
    await session.commit()
    await session.refresh(row)
    return _to_out(row)


async def update_integration(
    session: AsyncSession,
    *,
    integration_id: uuid.UUID,
    body: ThirdPartyApiUpdate,
    actor_id: uuid.UUID,
) -> ThirdPartyApiOut:
    row = await session.get(ThirdPartyApi, integration_id)
    if row is None:
        raise ValidationError("API integration not found")

    if body.name is not None and body.name.strip() != row.name:
        clash = (
            await session.execute(
                select(ThirdPartyApi).where(
                    ThirdPartyApi.name == body.name.strip(), ThirdPartyApi.id != row.id
                )
            )
        ).scalar_one_or_none()
        if clash is not None:
            raise ValidationError(f"An API integration named '{body.name}' already exists")
        row.name = body.name.strip()
    if body.description is not None:
        row.description = body.description
    if body.base_url is not None:
        row.base_url = body.base_url.strip()
    if body.method is not None:
        row.method = body.method
    if body.code is not None:
        row.code = body.code or None
    if body.api_key:
        row.encrypted_key = encrypt_secret(body.api_key)
        row.key_fingerprint = fingerprint(body.api_key)
    if body.enabled is not None:
        row.enabled = body.enabled
    await record_audit(
        session,
        action="settings.integration_updated",
        actor_id=actor_id,
        resource_type="third_party_api",
        resource_id=str(row.id),
        details={"name": row.name, "enabled": row.enabled},
    )
    await session.commit()
    await session.refresh(row)
    return _to_out(row)


async def delete_integration(
    session: AsyncSession,
    *,
    integration_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> None:
    row = await session.get(ThirdPartyApi, integration_id)
    if row is None:
        raise ValidationError("API integration not found")
    name = row.name
    await session.delete(row)
    await record_audit(
        session,
        action="settings.integration_deleted",
        actor_id=actor_id,
        resource_type="third_party_api",
        resource_id=str(integration_id),
        details={"name": name},
    )
    await session.commit()


def resolve_api_key(row: ThirdPartyApi) -> str:
    return decrypt_secret(row.encrypted_key) if row.encrypted_key else ""
