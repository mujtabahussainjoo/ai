#!/usr/bin/env python3
"""Re-run document ingestion for uploaded files.

Rebuilds the text chunks for documents that are missing them or need
re-processing after a configuration change.  Run from apps/backend/:

  ./.venv/bin/python ../../scripts/ingest_documents.py --all
  ./.venv/bin/python ../../scripts/ingest_documents.py --doc-id <UUID>
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure the ``app`` package is importable when invoked from the repo root.
_BACKEND_ROOT = Path(__file__).resolve().parents[1] / "apps" / "backend"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy import select  # noqa: E402

from app.core.logging import setup_logging  # noqa: E402
from app.db.models import Document  # noqa: E402
from app.db.session import async_session_factory, dispose_engine  # noqa: E402
from app.services.documents import reingest_document  # noqa: E402


async def reingest_all() -> None:
    async with async_session_factory() as session:
        stmt = select(Document).where(Document.deleted_at.is_(None)).order_by(Document.created_at.desc())
        result = await session.execute(stmt)
        docs = list(result.scalars().all())
    if not docs:
        print("No documents found to re-ingest.")
        return

    async with async_session_factory() as session:
        for doc in docs:
            out = await reingest_document(session, doc)
            await session.commit()
            await session.refresh(doc)
            chunks = out.chunk_count
            print(f"  [{doc.status:>10}]  {doc.filename!r}  ({chunks} chunks)")


async def reingest_one(doc_id: str) -> None:
    import uuid as _uuid  # noqa: E402
    from app.core.exceptions import NotFoundError  # noqa: E402

    target = _uuid.UUID(doc_id)
    async with async_session_factory() as session:
        doc = await session.get(Document, target)
        if doc is None or doc.deleted_at is not None:
            raise NotFoundError(f"Document {doc_id} not found")
        out = await reingest_document(session, doc)
        await session.commit()
        await session.refresh(doc)
        print(f"  [{doc.status:>10}]  {doc.filename!r}  ({out.chunk_count} chunks)")


def main() -> None:
    setup_logging("INFO")
    parser = argparse.ArgumentParser(description="Re-run document ingestion.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Re-ingest all documents")
    group.add_argument("--doc-id", type=str, help="UUID of a single document to re-ingest")
    args = parser.parse_args()
    if args.all:
        asyncio.run(reingest_all())
    else:
        asyncio.run(reingest_one(args.doc_id))


if __name__ == "__main__":
    main()
