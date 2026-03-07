"""add and align audit_logs schema

Revision ID: 003_add_audit_log
Revises: 001_initial_migration
Create Date: 2026-03-07 11:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "003_add_audit_log"
down_revision = "001_initial_migration"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _colmap(inspector: sa.Inspector, table_name: str) -> dict[str, dict]:
    return {col["name"]: col for col in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("action", sa.String(length=50), nullable=False),
            sa.Column("resource_type", sa.String(length=30), nullable=True),
            sa.Column("resource_id", sa.Integer(), nullable=True),
            sa.Column("details", sa.JSON(), nullable=True),
            sa.Column("ip_address", sa.String(length=45), nullable=True),
            sa.Column("user_agent", sa.Text(), nullable=True),
            sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
        op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
        op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"], unique=False)
        op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"], unique=False)
        op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)
        return

    cols = _colmap(inspector, "audit_logs")

    if "action" in cols:
        op.alter_column("audit_logs", "action", existing_type=sa.String(length=100), type_=sa.String(length=50))

    if "resource_type" not in cols:
        op.add_column("audit_logs", sa.Column("resource_type", sa.String(length=30), nullable=True))
        op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"], unique=False)

    if "resource_id" not in cols:
        op.add_column("audit_logs", sa.Column("resource_id", sa.Integer(), nullable=True))
        op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)

    if "ip_address" not in cols:
        op.add_column("audit_logs", sa.Column("ip_address", sa.String(length=45), nullable=True))

    if "user_agent" not in cols:
        op.add_column("audit_logs", sa.Column("user_agent", sa.Text(), nullable=True))

    cols = _colmap(sa.inspect(bind), "audit_logs")

    if "metadata" in cols:
        if "details" in cols:
            # Existing schema had `details` as TEXT and `metadata` as JSON.
            op.drop_column("audit_logs", "details")
        op.alter_column("audit_logs", "metadata", new_column_name="details", existing_type=sa.JSON())
    else:
        if "details" not in cols:
            op.add_column("audit_logs", sa.Column("details", sa.JSON(), nullable=True))
        else:
            # Best-effort type alignment: keep existing values when possible.
            if not isinstance(cols["details"]["type"], sa.JSON):
                op.execute("ALTER TABLE audit_logs ALTER COLUMN details TYPE JSON USING to_json(details)")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "audit_logs"):
        return

    cols = _colmap(inspector, "audit_logs")

    if "details" in cols:
        # Revert to previous naming convention used by initial migration.
        op.alter_column("audit_logs", "details", new_column_name="metadata", existing_type=sa.JSON())
        op.add_column("audit_logs", sa.Column("details", sa.Text(), nullable=True))

    if "resource_id" in cols:
        op.drop_index("ix_audit_logs_resource_id", table_name="audit_logs")
        op.drop_column("audit_logs", "resource_id")

    if "resource_type" in cols:
        op.drop_index("ix_audit_logs_resource_type", table_name="audit_logs")
        op.drop_column("audit_logs", "resource_type")

    if "ip_address" in cols:
        op.drop_column("audit_logs", "ip_address")

    if "user_agent" in cols:
        op.drop_column("audit_logs", "user_agent")

    op.alter_column("audit_logs", "action", existing_type=sa.String(length=50), type_=sa.String(length=100))

