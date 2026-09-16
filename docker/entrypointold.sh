#!/bin/sh
# Backend container entrypoint:
#  1. Wait for PostgreSQL to accept connections,
#  2. Apply pending Alembic migrations,
#  3. Execute the container CMD (uvicorn app.main:app ...).
set -e

echo "[entrypoint] Waiting for PostgreSQL..."
python - <<'PY' || exit 1
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def wait_for_db(attempts: int = 30, delay: float = 2.0) -> None:
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    for i in range(attempts):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            return
        except Exception as exc:  # noqa: BLE001
            print(f"  [entrypoint] db not ready ({i + 1}/{attempts}): {exc}")
            await asyncio.sleep(delay)
    await engine.dispose()
    sys.exit(1)


asyncio.run(wait_for_db())
PY

echo "[entrypoint] Applying migrations (alembic upgrade head)..."
alembic upgrade head

echo "[entrypoint] Seeding roles (idempotent)..."
python - <<'PY'
import asyncio
from app.db.seeds import run_seeds
from app.db.session import async_session_factory

async def seed():
    async with async_session_factory() as session:
        await run_seeds(session)
        await session.commit()

asyncio.run(seed())
PY

echo "[entrypoint] Starting: $*"
exec "$@"