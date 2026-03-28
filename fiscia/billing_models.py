"""
SQLAlchemy models for Stripe billing integration.

4 models: SubscriptionPlan, FirmSubscription, UsageCredit, BillingEvent.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from fiscia.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _new_uuid():
    return str(uuid.uuid4())


class SubscriptionPlan(Base):
    """Available subscription tiers (Starter / Pro / Cabinet)."""
    __tablename__ = "subscription_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    stripe_price_id: Mapped[str] = mapped_column(String(100), nullable=False)
    price_eur: Mapped[float] = mapped_column(Float, nullable=False)
    calculation_limit: Mapped[int] = mapped_column(Integer, nullable=True)  # None = unlimited
    user_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class FirmSubscription(Base):
    """Active subscription linking a firm to a Stripe subscription."""
    __tablename__ = "firm_subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    firm_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    plan_id: Mapped[str] = mapped_column(String(36), nullable=False)
    stripe_customer_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="incomplete"
    )  # active, past_due, canceled, incomplete, trialing
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    trial_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class UsageCredit(Base):
    """Monthly usage tracking for calculation limits."""
    __tablename__ = "usage_credits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    firm_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    credits_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    credits_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_usage_firm_period", "firm_id", "period_start"),
    )


class BillingEvent(Base):
    """Audit trail for all billing events from Stripe."""
    __tablename__ = "billing_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    firm_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    stripe_event_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=True, default="eur")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="processed")
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    __table_args__ = (
        Index("ix_billing_event_type", "event_type"),
        Index("ix_billing_created", "created_at"),
    )
