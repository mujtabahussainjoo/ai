"""make base_url nullable on third_party_apis

Revision ID: 82c78f737119
Revises: c4d5e6f7081a
Create Date: 2026-09-16 05:35:00.000000
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "82c78f737119"
down_revision: str | None = "c4d5e6f7081a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("third_party_apis", "base_url", existing_type=sa.String(length=500), nullable=True)


def downgrade() -> None:
    op.alter_column("third_party_apis", "base_url", existing_type=sa.String(length=500), nullable=False)
