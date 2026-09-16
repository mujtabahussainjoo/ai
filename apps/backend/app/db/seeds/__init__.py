"""Database seeders."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .roles import seed_roles  # noqa: F401


async def run_seeds(session: AsyncSession) -> None:
    await seed_roles(session)
