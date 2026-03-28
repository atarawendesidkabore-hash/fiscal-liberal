"""Initial tables: users, liasse_calculations, cgi_articles

Revision ID: 001
Revises: None
Create Date: 2026-03-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "liasse_calculations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("siren", sa.String(9), nullable=False),
        sa.Column("exercice_clos", sa.String(10), nullable=False),
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.Column("result_data", sa.JSON(), nullable=False),
        sa.Column("rf_brut", sa.Float(), nullable=False),
        sa.Column("rf_net", sa.Float(), nullable=False),
        sa.Column("is_total", sa.Float(), nullable=False),
        sa.Column("regime", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_liasse_user_id", "liasse_calculations", ["user_id"])
    op.create_index("ix_liasse_siren", "liasse_calculations", ["siren"])
    op.create_index("ix_liasse_siren_exercice", "liasse_calculations", ["siren", "exercice_clos"])

    op.create_table(
        "cgi_articles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("article", sa.String(50), unique=True, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("cgi_articles")
    op.drop_table("liasse_calculations")
    op.drop_table("users")
