"""FastAPI dependencies for authentication and authorization."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import decode_token
from app.db.models import User
from app.db.repositories.user import UserRepository
from app.db.session import get_db


async def _extract_bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise AuthError("Missing bearer token")
    token = header.removeprefix("Bearer ").strip()
    if not token:
        raise AuthError("Missing bearer token")
    return token


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = await _extract_bearer_token(request)
    try:
        payload = decode_token(token, expected_type="access")
    except Exception as exc:
        raise AuthError("Invalid or expired access token") from exc

    user_id = uuid.UUID(payload["sub"])
    user = await UserRepository(db).get(user_id)
    if user is None or not user.is_active:
        raise AuthError("Invalid or expired access token")
    return user


def require_roles(*roles: str) -> Callable[..., Any]:
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {role.name for role in current_user.roles}
        if not user_roles.intersection(set(roles)):
            raise ForbiddenError("You do not have permission for this action")
        return current_user

    return dependency


require_admin = require_roles("admin")
require_user = require_roles("user", "admin")


def get_current_user_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user
