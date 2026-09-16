"""add method and code columns to third_party_apis

Revision ID: c4d5e6f7081a
Revises: b3c4d5e6f708
Create Date: 2026-09-16 05:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4d5e6f7081a"
down_revision: str | None = "b3c4d5e6f708"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("third_party_apis", sa.Column("method", sa.String(length=12), nullable=False, server_default="GET"))
    op.add_column("third_party_apis", sa.Column("code", sa.Text(), nullable=True))
    op.alter_column("third_party_apis", "method", server_default=None)


def downgrade() -> None:
    op.drop_column("third_party_apis", "code")
    op.drop_column("third_party_apis", "method")
