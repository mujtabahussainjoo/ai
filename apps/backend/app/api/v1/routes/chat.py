"""Chat and conversation endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps.auth import get_current_user
from app.core.config import settings
from app.core.limits import limiter
from app.db.models import User
from app.db.session import get_db
from app.schemas.chat import (
    ChatRequest,
    ConversationCreate,
    ConversationSummary,
    MessageOut,
)
from app.schemas.common import envelope
from app.services import chat as chat_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=dict[str, Any])
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def list_conversations(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await chat_service.list_conversations(
        db, user_id=current_user.id, page=page, page_size=page_size
    )
    return envelope(
        {
            "items": [ConversationSummary.model_validate(c).model_dump(mode="json") for c in result.items],
            "page": result.page,
            "page_size": result.page_size,
            "total": result.total,
            "total_pages": result.total_pages,
        }
    )


@router.post("", response_model=dict[str, Any])
async def create_conversation(
    body: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    conversation = await chat_service.create_conversation(db, user_id=current_user.id, body=body)
    return envelope(ConversationSummary.model_validate(conversation).model_dump(mode="json"))


@router.get("/{conversation_id}", response_model=dict[str, Any])
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    import uuid as _uuid  # noqa: PLC0415

    from app.db.repositories.conversation import MessageRepository  # noqa: PLC0415

    conversation = await chat_service.get_conversation_detail(
        db, user_id=current_user.id, conversation_id=_uuid.UUID(conversation_id)
    )
    messages = await MessageRepository(db).all_for_conversation(conversation.id)
    detail = ConversationSummary.model_validate(conversation).model_dump(mode="json")
    detail["messages"] = [MessageOut.model_validate(m).model_dump(mode="json") for m in messages]
    return envelope(detail)


@router.delete("/{conversation_id}", response_model=dict[str, Any])
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    import uuid as _uuid  # noqa: PLC0415

    await chat_service.delete_conversation(
        db, user_id=current_user.id, conversation_id=_uuid.UUID(conversation_id)
    )
    return envelope({"status": "ok"})


@router.get("/{conversation_id}/messages", response_model=dict[str, Any])
async def list_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    import uuid as _uuid  # noqa: PLC0415

    from app.db.repositories.conversation import MessageRepository  # noqa: PLC0415

    conv = await chat_service.get_conversation_detail(
        db, user_id=current_user.id, conversation_id=_uuid.UUID(conversation_id)
    )
    messages = await MessageRepository(db).all_for_conversation(conv.id)
    return envelope([MessageOut.model_validate(m).model_dump(mode="json") for m in messages])


@router.post("/{conversation_id}/messages", response_model=dict[str, Any])
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def send_message(
    request: Request,
    conversation_id: str,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    import uuid as _uuid  # noqa: PLC0415

    result = await chat_service.send_message(
        db,
        user_id=current_user.id,
        conversation_id=_uuid.UUID(conversation_id),
        body=body,
    )
    return envelope(result.model_dump(mode="json"))


@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    import uuid as _uuid  # noqa: PLC0415

    async def generate() -> Any:
        async for chunk in chat_service.stream_message(
            db,
            user_id=current_user.id,
            conversation_id=_uuid.UUID(conversation_id),
            body=body,
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")
