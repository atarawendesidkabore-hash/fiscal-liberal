"""add subscription plans + firm billing tables

Revision ID: 005_add_billing_tables
Revises: 004_auth_rbac
Create Date: 2026-03-07 15:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "005_add_billing_tables"
down_revision = "004_auth_rbac"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "subscription_plans"):
        op.create_table(
            "subscription_plans",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(length=32), nullable=False),
            sa.Column("stripe_price_id", sa.String(length=128), nullable=False),
            sa.Column("price", sa.Numeric(10, 2), nullable=False),
            sa.Column("calculation_limit", sa.Integer(), nullable=False, server_default="-1"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("name", name="uq_subscription_plans_name"),
            sa.UniqueConstraint("stripe_price_id", name="uq_subscription_plans_stripe_price_id"),
        )
        op.create_index("ix_subscription_plans_name", "subscription_plans", ["name"], unique=True)
        op.create_index("ix_subscription_plans_stripe_price_id", "subscription_plans", ["stripe_price_id"], unique=True)

        op.execute(
            """
            INSERT INTO subscription_plans (name, stripe_price_id, price, calculation_limit)
            VALUES
              ('starter', 'price_starter_monthly', 29.00, 50),
              ('pro', 'price_pro_monthly', 79.00, -1),
              ('cabinet', 'price_cabinet_monthly', 199.00, -1)
            """
        )

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "firm_subscriptions"):
        op.create_table(
            "firm_subscriptions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("firm_id", sa.Integer(), nullable=False),
            sa.Column("stripe_customer_id", sa.String(length=128), nullable=False),
            sa.Column("stripe_subscription_id", sa.String(length=128), nullable=False),
            sa.Column("plan_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="incomplete"),
            sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
            sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["firm_id"], ["firms.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["plan_id"], ["subscription_plans.id"], ondelete="RESTRICT"),
            sa.UniqueConstraint("firm_id", name="uq_firm_subscriptions_firm_id"),
            sa.UniqueConstraint("stripe_subscription_id", name="uq_firm_subscriptions_stripe_subscription_id"),
        )
        op.create_index("ix_firm_subscriptions_firm_id", "firm_subscriptions", ["firm_id"], unique=True)
        op.create_index("ix_firm_subscriptions_stripe_customer_id", "firm_subscriptions", ["stripe_customer_id"], unique=False)
        op.create_index("ix_firm_subscriptions_stripe_subscription_id", "firm_subscriptions", ["stripe_subscription_id"], unique=True)
        op.create_index("ix_firm_subscriptions_plan_id", "firm_subscriptions", ["plan_id"], unique=False)

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "usage_credits"):
        op.create_table(
            "usage_credits",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("firm_id", sa.Integer(), nullable=False),
            sa.Column("credits_total", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("credits_used", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("period", sa.String(length=7), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["firm_id"], ["firms.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("firm_id", "period", name="uq_usage_credits_firm_period"),
        )
        op.create_index("ix_usage_credits_firm_id", "usage_credits", ["firm_id"], unique=False)
        op.create_index("ix_usage_credits_period", "usage_credits", ["period"], unique=False)

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "billing_events"):
        op.create_table(
            "billing_events",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("firm_id", sa.Integer(), nullable=True),
            sa.Column("stripe_event_id", sa.String(length=128), nullable=False),
            sa.Column("type", sa.String(length=128), nullable=False),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="received"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["firm_id"], ["firms.id"], ondelete="SET NULL"),
            sa.UniqueConstraint("stripe_event_id", name="uq_billing_events_stripe_event_id"),
        )
        op.create_index("ix_billing_events_firm_id", "billing_events", ["firm_id"], unique=False)
        op.create_index("ix_billing_events_stripe_event_id", "billing_events", ["stripe_event_id"], unique=True)
        op.create_index("ix_billing_events_type", "billing_events", ["type"], unique=False)
        op.create_index("ix_billing_events_status", "billing_events", ["status"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "billing_events"):
        op.drop_index("ix_billing_events_status", table_name="billing_events")
        op.drop_index("ix_billing_events_type", table_name="billing_events")
        op.drop_index("ix_billing_events_stripe_event_id", table_name="billing_events")
        op.drop_index("ix_billing_events_firm_id", table_name="billing_events")
        op.drop_table("billing_events")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "usage_credits"):
        op.drop_index("ix_usage_credits_period", table_name="usage_credits")
        op.drop_index("ix_usage_credits_firm_id", table_name="usage_credits")
        op.drop_table("usage_credits")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "firm_subscriptions"):
        op.drop_index("ix_firm_subscriptions_plan_id", table_name="firm_subscriptions")
        op.drop_index("ix_firm_subscriptions_stripe_subscription_id", table_name="firm_subscriptions")
        op.drop_index("ix_firm_subscriptions_stripe_customer_id", table_name="firm_subscriptions")
        op.drop_index("ix_firm_subscriptions_firm_id", table_name="firm_subscriptions")
        op.drop_table("firm_subscriptions")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "subscription_plans"):
        op.drop_index("ix_subscription_plans_stripe_price_id", table_name="subscription_plans")
        op.drop_index("ix_subscription_plans_name", table_name="subscription_plans")
        op.drop_table("subscription_plans")