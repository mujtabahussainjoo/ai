"""Common response envelope and pagination helpers."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


def envelope(data: Any) -> dict[str, Any]:
    return {"data": data, "error": None}


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str | None = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size


class Paginated(BaseModel, Generic[T]):  # noqa: UP046
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def from_page(cls, items: list[T], total: int, page: int, page_size: int) -> Paginated[T]:
        return cls(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if page_size else 0,
        )
