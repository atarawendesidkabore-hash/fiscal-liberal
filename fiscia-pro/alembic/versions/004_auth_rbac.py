"""add auth and rbac tables

Revision ID: 004_auth_rbac
Revises: 003_add_audit_log
Create Date: 2026-03-07 12:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "004_auth_rbac"
down_revision = "003_add_audit_log"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _colmap(inspector: sa.Inspector, table_name: str) -> dict[str, dict]:
    return {col["name"]: col for col in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "firms"):
        op.create_table(
            "firms",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("plan_type", sa.String(length=32), nullable=False, server_default="starter"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_firms_name", "firms", ["name"], unique=True)

    inspector = sa.inspect(bind)
    user_cols = _colmap(inspector, "users")

    if "hashed_password" not in user_cols:
        op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))
        op.execute("UPDATE users SET hashed_password = 'migration_placeholder' WHERE hashed_password IS NULL")
        op.alter_column("users", "hashed_password", nullable=False)

    if "firm_id" not in user_cols:
        op.add_column("users", sa.Column("firm_id", sa.Integer(), nullable=True))

        op.execute(
            """
            INSERT INTO firms (name, plan_type)
            SELECT 'Migration Firm', 'starter'
            WHERE NOT EXISTS (SELECT 1 FROM firms)
            """
        )
        op.execute(
            "UPDATE users SET firm_id = (SELECT id FROM firms ORDER BY id ASC LIMIT 1) WHERE firm_id IS NULL"
        )

        op.create_foreign_key("fk_users_firm_id", "users", "firms", ["firm_id"], ["id"], ondelete="CASCADE")
        op.create_index("ix_users_firm_id", "users", ["firm_id"], unique=False)
        op.alter_column("users", "firm_id", nullable=False)

    if not _table_exists(inspector, "refresh_tokens"):
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("jti", sa.String(length=64), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"], unique=True)
        op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
        op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"], unique=False)

    inspector = sa.inspect(bind)
    liasse_cols = _colmap(inspector, "liasse_calculations")
    if "firm_id" not in liasse_cols:
        op.add_column("liasse_calculations", sa.Column("firm_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_liasse_calculations_firm_id",
            "liasse_calculations",
            "firms",
            ["firm_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index("ix_liasse_calculations_firm_id", "liasse_calculations", ["firm_id"], unique=False)

    inspector = sa.inspect(bind)
    audit_cols = _colmap(inspector, "audit_logs")
    if "firm_id" not in audit_cols:
        op.add_column("audit_logs", sa.Column("firm_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_audit_logs_firm_id", "audit_logs", "firms", ["firm_id"], ["id"], ondelete="SET NULL")
        op.create_index("ix_audit_logs_firm_id", "audit_logs", ["firm_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "audit_logs"):
        cols = _colmap(inspector, "audit_logs")
        if "firm_id" in cols:
            op.drop_index("ix_audit_logs_firm_id", table_name="audit_logs")
            op.drop_constraint("fk_audit_logs_firm_id", "audit_logs", type_="foreignkey")
            op.drop_column("audit_logs", "firm_id")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "liasse_calculations"):
        cols = _colmap(inspector, "liasse_calculations")
        if "firm_id" in cols:
            op.drop_index("ix_liasse_calculations_firm_id", table_name="liasse_calculations")
            op.drop_constraint("fk_liasse_calculations_firm_id", "liasse_calculations", type_="foreignkey")
            op.drop_column("liasse_calculations", "firm_id")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "refresh_tokens"):
        op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")
        op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
        op.drop_index("ix_refresh_tokens_jti", table_name="refresh_tokens")
        op.drop_table("refresh_tokens")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "users"):
        cols = _colmap(inspector, "users")
        if "firm_id" in cols:
            op.drop_index("ix_users_firm_id", table_name="users")
            op.drop_constraint("fk_users_firm_id", "users", type_="foreignkey")
            op.drop_column("users", "firm_id")
        if "hashed_password" in cols:
            op.drop_column("users", "hashed_password")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "firms"):
        op.drop_index("ix_firms_name", table_name="firms")
        op.drop_table("firms")