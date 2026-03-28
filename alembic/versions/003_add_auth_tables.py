"""Add firms, token_blacklist tables and auth columns to users

Revision ID: 003
Revises: 002
Create Date: 2026-03-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- firms table ---
    op.create_table(
        "firms",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("siren", sa.String(9), unique=True, nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    # --- users: add auth columns ---
    op.add_column("users", sa.Column("hashed_password", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("full_name", sa.String(200), nullable=True))
    op.add_column("users", sa.Column("role", sa.String(20), nullable=True, server_default="client"))
    op.add_column("users", sa.Column("firm_id", sa.String(36), nullable=True))
    op.create_index("ix_users_firm_id", "users", ["firm_id"])

    # --- token_blacklist table ---
    op.create_table(
        "token_blacklist",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("jti", sa.String(36), unique=True, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_token_blacklist_jti", "token_blacklist", ["jti"])


def downgrade() -> None:
    op.drop_table("token_blacklist")
    op.drop_index("ix_users_firm_id", table_name="users")
    op.drop_column("users", "firm_id")
    op.drop_column("users", "role")
    op.drop_column("users", "full_name")
    op.drop_column("users", "hashed_password")
    op.drop_table("firms")
