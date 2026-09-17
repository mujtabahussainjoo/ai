"""Document upload and management endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import get_current_user, require_admin
from app.core.config import settings
from app.core.limits import limiter
from app.db.models import User
from app.db.repositories.document import DocumentChunkRepository, DocumentRepository
from app.db.session import get_db
from app.schemas.common import envelope
from app.schemas.documents import DocumentSummaryOut
from app.services import documents as documents_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=dict[str, Any])
async def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    docs, total = await DocumentRepository(db).list_all(page=page, page_size=page_size)
    items = []
    for doc in docs:
        row = DocumentSummaryOut.model_validate(doc).model_dump(mode="json")
        row["chunk_count"] = await DocumentChunkRepository(db).count_for_document(doc.id)
        items.append(row)
    return envelope(
        {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size if page_size else 0,
        }
    )


@router.post("", response_model=dict[str, Any])
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await documents_service.save_upload(
        db,
        owner_id=current_user.id,
        upload=file,
    )
    row = DocumentSummaryOut.model_validate(result.document).model_dump(mode="json")
    row["chunk_count"] = result.chunk_count
    await db.commit()
    await db.refresh(result.document)
    return envelope(row)


@router.delete("/{document_id}", response_model=dict[str, Any])
async def delete_document(
    document_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await documents_service.delete_document(
        db,
        document_id=uuid.UUID(document_id),
    )
    return envelope({"status": "ok"})
