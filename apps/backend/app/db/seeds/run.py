"""Seed default roles/permissions: python -m app.db.seeds.run."""

from __future__ import annotations

import asyncio

from app.db.seeds import run_seeds
from app.db.session import async_session_factory, dispose_engine


async def main() -> None:
    async with async_session_factory() as session:
        await run_seeds(session)
        await session.commit()
        print("seeded roles and permissions")
    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
