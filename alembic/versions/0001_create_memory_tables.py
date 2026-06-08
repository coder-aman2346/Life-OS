"""create memory tables

Revision ID: 0001_create_memory_tables
Revises:
Create Date: 2026-06-05 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "0001_create_memory_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_last_active"), "sessions", ["last_active"], unique=False)
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_created_at"), "messages", ["created_at"], unique=False)
    op.create_index(op.f("ix_messages_session_id"), "messages", ["session_id"], unique=False)

    op.create_table(
        "memory_fragments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("source_session", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_session"], ["sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_memory_fragments_created_at"), "memory_fragments", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_memory_fragments_source_session"),
        "memory_fragments",
        ["source_session"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_fragments_user_id"), "memory_fragments", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_memory_fragments_user_id"), table_name="memory_fragments")
    op.drop_index(op.f("ix_memory_fragments_source_session"), table_name="memory_fragments")
    op.drop_index(op.f("ix_memory_fragments_created_at"), table_name="memory_fragments")
    op.drop_table("memory_fragments")
    op.drop_index(op.f("ix_messages_session_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_created_at"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_last_active"), table_name="sessions")
    op.drop_table("sessions")
