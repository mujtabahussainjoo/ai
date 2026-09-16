"""Conversation and message repositories."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from app.core.exceptions import NotFoundError
from app.db.models import Conversation, Message

from .base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Conversation], int]:
        filters = [Conversation.user_id == user_id, Conversation.deleted_at.is_(None)]
        items, total = await self.paginate(
            filters=filters,
            sort_by="updated_at",
            sort_order="desc",
            page=page,
            page_size=page_size,
        )
        return items, total

    async def get_owned(self, user_id: uuid.UUID, conversation_id: uuid.UUID) -> Conversation:
        conversation = await self.get(conversation_id)
        if conversation is None or conversation.user_id != user_id or conversation.deleted_at is not None:
            raise NotFoundError("Conversation not found")
        return conversation

    async def soft_delete(self, conversation: Conversation) -> None:
        conversation.deleted_at = datetime.now(UTC)
        await self.session.flush()


class MessageRepository(BaseRepository[Message]):
    model = Message

    async def all_for_conversation(self, conversation_id: uuid.UUID) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def history(self, conversation_id: uuid.UUID, *, max_messages: int = 30) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_messages)
        )
        rows = list((await self.session.execute(stmt)).scalars().all())
        rows.reverse()
        return rows

    async def add(
        self,
        *,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        model: str | None = None,
        token_usage: dict[str, Any] | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            token_usage=token_usage,
        )
        self.session.add(message)
        return message
