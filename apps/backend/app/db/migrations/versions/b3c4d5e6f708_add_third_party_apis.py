"""add third_party_apis

Revision ID: b3c4d5e6f708
Revises: 546103fab6c1
Create Date: 2026-09-16 05:20:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b3c4d5e6f708"
down_revision: str | None = "546103fab6c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "third_party_apis",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("base_url", sa.String(length=500), nullable=False),
        sa.Column("auth_type", sa.String(length=30), nullable=False),
        sa.Column("header_name", sa.String(length=120), nullable=True),
        sa.Column("encrypted_key", postgresql.BYTEA(), nullable=True),
        sa.Column("key_fingerprint", sa.String(length=64), nullable=True),
        sa.Column("extra_headers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_third_party_apis")),
    )
    op.create_index(op.f("ix_third_party_apis_name"), "third_party_apis", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_third_party_apis_name"), table_name="third_party_apis")
    op.drop_table("third_party_apis")
