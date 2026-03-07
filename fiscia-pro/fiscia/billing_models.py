from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fiscia.models_db import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    stripe_price_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    calculation_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=-1, server_default="-1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    subscriptions: Mapped[list["FirmSubscription"]] = relationship("FirmSubscription", back_populates="plan")


class FirmSubscription(Base):
    __tablename__ = "firm_subscriptions"
    __table_args__ = (UniqueConstraint("firm_id", name="uq_firm_subscriptions_firm_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_customer_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("subscription_plans.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="incomplete", server_default="incomplete", index=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), server_default=func.now()
    )

    firm: Mapped["Firm"] = relationship("Firm", backref="firm_subscriptions")
    plan: Mapped[SubscriptionPlan] = relationship("SubscriptionPlan", back_populates="subscriptions")


class UsageCredit(Base):
    __tablename__ = "usage_credits"
    __table_args__ = (UniqueConstraint("firm_id", "period", name="uq_usage_credits_firm_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id", ondelete="CASCADE"), nullable=False, index=True)
    credits_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    credits_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    period: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    firm: Mapped["Firm"] = relationship("Firm", backref="usage_credits")


class BillingEvent(Base):
    __tablename__ = "billing_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stripe_event_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    firm_id: Mapped[int | None] = mapped_column(ForeignKey("firms.id", ondelete="SET NULL"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0, server_default="0")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="received", server_default="received", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    firm: Mapped["Firm | None"] = relationship("Firm", backref="billing_events")


# Backward compatibility aliases for previous internal naming.
Subscription = FirmSubscription
PaymentEvent = BillingEvent