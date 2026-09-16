"""Business logic for authentication."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.db.repositories.user import (
    RoleRepository,
    SessionRepository,
    UserRepository,
    hash_refresh_token,
)
from app.services.audit import record_audit

refresh_ttl = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
access_ttl_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


async def register_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    display_name: str | None,
    ip_address: str | None = None,
    requested_roles: list[str] | None = None,
) -> User:
    user_repo = UserRepository(session)
    role_repo = RoleRepository(session)
    if await user_repo.get_by_email(email):
        raise AuthError("An account already exists for this email")
    is_first = (await user_repo.paginate(page=1, page_size=1))[1] == 0
    role_names = ["admin"] if is_first else ["user"]
    if requested_roles and not settings.is_production:
        role_names = requested_roles
    roles = await role_repo.get_by_names(role_names)
    known = {role.name for role in roles}
    missing = set(role_names) - known
    if missing:
        raise AuthError(f"Required roles not seeded: {sorted(missing)}; run seed_roles first")
    user = await user_repo.create(
        email=email,
        password_hash=hash_password(password),
        display_name=display_name,
        roles=roles,
    )
    await session.flush()
    await record_audit(
        session,
        action="auth.register",
        actor_id=user.id,
        resource_type="user",
        resource_id=str(user.id),
        ip_address=ip_address,
    )
    await session.commit()
    await session.refresh(user)
    return user


async def issue_tokens(
    session: AsyncSession, *, user: User, ip_address: str | None = None, user_agent: str | None = None
) -> dict[str, Any]:
    access_token = create_access_token(user.id, extra={"roles": [role.name for role in user.roles]})
    refresh_token = create_refresh_token(user.id)
    session_repo = SessionRepository(session)
    await session_repo.create(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC) + refresh_ttl,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await session.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_ttl_seconds),
    }


async def login_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict[str, Any]:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password")
    if not user.is_active:
        raise AuthError("Account is disabled")
    await record_audit(
        session,
        action="auth.login",
        actor_id=user.id,
        resource_type="user",
        resource_id=str(user.id),
        ip_address=ip_address,
    )
    return await issue_tokens(session, user=user, ip_address=ip_address, user_agent=user_agent)


async def refresh_tokens(
    session: AsyncSession, *, refresh_token: str, ip_address: str | None = None
) -> dict[str, Any]:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except Exception as exc:
        raise AuthError("Invalid or expired refresh token") from exc
    user_id = uuid.UUID(payload["sub"])
    session_repo = SessionRepository(session)
    stored = await session_repo.get_by_hash(hash_refresh_token(refresh_token))
    user_repo = UserRepository(session)
    user = await user_repo.get(user_id)
    if not stored or not user or stored.revoked_at is not None or stored.expires_at < datetime.now(UTC):
        raise AuthError("Invalid or expired refresh token")
    await session_repo.revoke(stored)
    return await issue_tokens(session, user=user, ip_address=ip_address)


async def change_password(
    session: AsyncSession, *, user: User, current_password: str, new_password: str
) -> None:
    if not verify_password(current_password, user.password_hash):
        raise AuthError("Current password is incorrect")
    user.password_hash = hash_password(new_password)
    await session.flush()
    await record_audit(
        session,
        action="auth.change_password",
        actor_id=user.id,
        resource_type="user",
        resource_id=str(user.id),
    )
    await SessionRepository(session).revoke_all_for_user(user.id)
    await session.commit()
