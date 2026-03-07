"""initial migration

Revision ID: 001_initial_migration
Revises:
Create Date: 2026-03-07 10:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "001_initial_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "liasse_calculations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("siren", sa.String(length=9), nullable=False),
        sa.Column("exercice_clos", sa.Date(), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_liasse_calculations_user_id", "liasse_calculations", ["user_id"], unique=False)
    op.create_index("ix_liasse_calculations_siren", "liasse_calculations", ["siren"], unique=False)
    op.create_index("ix_liasse_calculations_exercice_clos", "liasse_calculations", ["exercice_clos"], unique=False)
    op.create_index("ix_liasse_calculations_created_at", "liasse_calculations", ["created_at"], unique=False)
    op.create_index(
        "ix_liasse_calculations_user_created",
        "liasse_calculations",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_liasse_calculations_siren_exercice",
        "liasse_calculations",
        ["siren", "exercice_clos"],
        unique=False,
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_timestamp", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_liasse_calculations_siren_exercice", table_name="liasse_calculations")
    op.drop_index("ix_liasse_calculations_user_created", table_name="liasse_calculations")
    op.drop_index("ix_liasse_calculations_created_at", table_name="liasse_calculations")
    op.drop_index("ix_liasse_calculations_exercice_clos", table_name="liasse_calculations")
    op.drop_index("ix_liasse_calculations_siren", table_name="liasse_calculations")
    op.drop_index("ix_liasse_calculations_user_id", table_name="liasse_calculations")
    op.drop_table("liasse_calculations")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

