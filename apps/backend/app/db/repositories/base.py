"""Async repository base with pagination, filtering, and sorting."""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

M = TypeVar("M", bound=Base)


class BaseRepository(Generic[M]):  # noqa: UP046
    model: type[M]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, object_id: uuid.UUID) -> M | None:
        return await self.session.get(self.model, object_id)

    async def exists(self, object_id: uuid.UUID) -> bool:
        return await self.get(object_id) is not None

    async def _count(self, stmt: Select[tuple[M]]) -> int:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        return int((await self.session.execute(count_stmt)).scalar_one())

    async def paginate(
        self,
        *,
        filters: list[Any] | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[M], int]:
        stmt: Select[tuple[M]] = select(self.model)
        if filters:
            stmt = stmt.where(*filters)
        total = await self._count(stmt)
        order_column = getattr(self.model, sort_by, None) if sort_by else None
        if order_column is not None:
            stmt = stmt.order_by(order_column.asc() if sort_order == "asc" else order_column.desc())
        else:
            model: Any = self.model
            stmt = stmt.order_by(model.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total
