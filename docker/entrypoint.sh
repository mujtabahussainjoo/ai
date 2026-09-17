#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Waiting for PostgreSQL..."

python - <<'PY'
import asyncio
import os
import sys
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

database_url = os.getenv("DATABASE_URL")

if not database_url:
    # Derive from POSTGRES_* parts (same logic as app.core.config).
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "myaibuddy")
    user = os.getenv("POSTGRES_USER", "myaibuddy")
    password = os.getenv("POSTGRES_PASSWORD", "")
    database_url = (
        f"postgresql+asyncpg://{user}:{quote_plus(password)}"
        f"@{host}:{port}/{db}"
    )
    print(f"[entrypoint] Derived DATABASE_URL from POSTGRES_* vars (host={host}, port={port})")

if not database_url:
    print("[entrypoint] ERROR: DATABASE_URL is not set.", file=sys.stderr)
    sys.exit(1)

# Render provides: postgresql://...
# SQLAlchemy async engine requires: postgresql+asyncpg://...
if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )

async def wait_for_db() -> None:
    for attempt in range(1, 31):
        engine = None

        try:
            engine = create_async_engine(
                database_url,
                pool_pre_ping=True,
            )

            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))

            print("[entrypoint] PostgreSQL is ready", flush=True)
            return

        except Exception as error:
            print(
                f"[entrypoint] db not ready ({attempt}/30): {error}",
                flush=True,
            )
            await asyncio.sleep(2)

        finally:
            if engine is not None:
                await engine.dispose()

    print(
        "[entrypoint] ERROR: PostgreSQL was not reachable after 30 attempts.",
        file=sys.stderr,
    )
    sys.exit(1)

asyncio.run(wait_for_db())
PY

echo "[entrypoint] Running migrations..."
alembic upgrade head

echo "[entrypoint] Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"