"""Idempotent role/permission bootstrap."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import Role
from app.db.models import Permission
from app.db.models import Role as RoleModel

ADMIN_PERMISSIONS: dict[str, str] = {
    "settings.read": "Read runtime settings",
    "settings.write": "Update runtime settings",
    "providers.manage": "Configure AI providers",
    "users.manage": "Manage users",
    "documents.read": "Read documents",
    "documents.write": "Upload/delete documents",
    "agents.run": "Run agents",
    "audit.read": "Read audit logs",
}

USER_PERMISSIONS: dict[str, str] = {
    "documents.read": "Read documents",
    "documents.write": "Upload/delete documents",
    "agents.run": "Run agents",
}


async def seed_roles(session: AsyncSession) -> None:
    existing_roles = (await session.execute(select(RoleModel))).scalars().all()
    role_map: dict[str, RoleModel] = {role.name: role for role in existing_roles}

    existing_perms = {p.code: p for p in (await session.execute(select(Permission))).scalars().all()}

    all_perms = {**ADMIN_PERMISSIONS, **USER_PERMISSIONS}
    for code, description in all_perms.items():
        perm = existing_perms.get(code)
        if perm is None:
            perm = Permission(code=code, description=description)
            session.add(perm)
            existing_perms[code] = perm

    await session.flush()

    for role_name in (Role.ADMIN, Role.USER):
        role = role_map.get(role_name)
        if role is None:
            role = RoleModel(name=role_name, description=f"Auto-created {role_name} role")
            session.add(role)
            role_map[role_name] = role
        desired = ADMIN_PERMISSIONS if role_name == Role.ADMIN else USER_PERMISSIONS
        role.permissions = [existing_perms[code] for code in desired]

    await session.flush()
