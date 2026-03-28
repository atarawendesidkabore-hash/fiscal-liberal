"""
Stripe service layer — all Stripe API interactions.

Functions are pure async wrappers around the Stripe SDK.
DB persistence is handled by callers (endpoints / webhooks).
"""
import logging
from datetime import datetime, timezone
from typing import Optional

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.billing_models import BillingEvent, UsageCredit
from fiscia.config.stripe_config import (
    BILLING_PORTAL_RETURN_URL,
    CHECKOUT_CANCEL_URL,
    CHECKOUT_SUCCESS_URL,
    GRACE_OVERAGE_PCT,
    PRICE_IDS,
    STRIPE_SECRET_KEY,
    TRIAL_DAYS,
)

logger = logging.getLogger("fiscia.stripe_service")

stripe.api_key = STRIPE_SECRET_KEY


# ── Customer management ──────────────────────────────────────────

async def create_customer(firm_name: str, email: str, firm_id: str) -> str:
    """Create a Stripe customer for a firm. Returns stripe_customer_id."""
    customer = stripe.Customer.create(
        name=firm_name,
        email=email,
        metadata={"firm_id": firm_id},
    )
    logger.info("Stripe customer created: %s for firm %s", customer.id, firm_id)
    return customer.id


# ── Checkout ─────────────────────────────────────────────────────

async def create_checkout_session(
    plan_name: str,
    stripe_customer_id: str,
    firm_id: str,
    trial: bool = False,
) -> str:
    """Create a Stripe Checkout Session. Returns the session URL."""
    price_id = PRICE_IDS.get(plan_name)
    if not price_id:
        raise ValueError(f"Unknown plan: {plan_name}")

    params: dict = {
        "customer": stripe_customer_id,
        "payment_method_types": ["card"],
        "line_items": [{"price": price_id, "quantity": 1}],
        "mode": "subscription",
        "success_url": CHECKOUT_SUCCESS_URL,
        "cancel_url": CHECKOUT_CANCEL_URL,
        "metadata": {"firm_id": firm_id, "plan": plan_name},
        "subscription_data": {"metadata": {"firm_id": firm_id, "plan": plan_name}},
    }
    if trial:
        params["subscription_data"]["trial_period_days"] = TRIAL_DAYS

    session = stripe.checkout.Session.create(**params)
    logger.info("Checkout session created: %s for plan %s", session.id, plan_name)
    return session.url


# ── Subscription lifecycle ───────────────────────────────────────

async def cancel_subscription(stripe_subscription_id: str) -> dict:
    """Cancel subscription at period end (no immediate revocation)."""
    sub = stripe.Subscription.modify(
        stripe_subscription_id,
        cancel_at_period_end=True,
    )
    logger.info("Subscription %s set to cancel at period end", stripe_subscription_id)
    return {
        "id": sub.id,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "current_period_end": datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc).isoformat(),
    }


async def update_subscription_plan(
    stripe_subscription_id: str, new_plan_name: str
) -> dict:
    """Change the plan on an existing subscription (prorate automatically)."""
    new_price_id = PRICE_IDS.get(new_plan_name)
    if not new_price_id:
        raise ValueError(f"Unknown plan: {new_plan_name}")

    sub = stripe.Subscription.retrieve(stripe_subscription_id)
    updated = stripe.Subscription.modify(
        stripe_subscription_id,
        items=[{"id": sub["items"]["data"][0].id, "price": new_price_id}],
        proration_behavior="create_prorations",
        metadata={"plan": new_plan_name},
    )
    logger.info("Subscription %s changed to %s", stripe_subscription_id, new_plan_name)
    return {
        "id": updated.id,
        "plan": new_plan_name,
        "status": updated.status,
    }


async def create_billing_portal_session(stripe_customer_id: str) -> str:
    """Create a Stripe Billing Portal session for payment method management."""
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=BILLING_PORTAL_RETURN_URL,
    )
    return session.url


# ── Usage tracking ───────────────────────────────────────────────

async def get_usage_for_firm(db: AsyncSession, firm_id: str) -> dict:
    """Get current period usage for a firm."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UsageCredit)
        .where(UsageCredit.firm_id == firm_id)
        .where(UsageCredit.period_start <= now)
        .where(UsageCredit.period_end > now)
    )
    usage = result.scalar_one_or_none()

    if usage is None:
        return {"credits_total": 0, "credits_used": 0, "credits_remaining": 0, "has_limit": False}

    remaining = max(0, usage.credits_total - usage.credits_used) if usage.credits_total > 0 else None
    return {
        "credits_total": usage.credits_total,
        "credits_used": usage.credits_used,
        "credits_remaining": remaining,
        "has_limit": usage.credits_total > 0,
        "period_start": usage.period_start.isoformat(),
        "period_end": usage.period_end.isoformat(),
    }


async def decrement_usage(db: AsyncSession, firm_id: str, amount: int = 1) -> dict:
    """Decrement usage credits. Returns new balance and whether limit is exceeded."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UsageCredit)
        .where(UsageCredit.firm_id == firm_id)
        .where(UsageCredit.period_start <= now)
        .where(UsageCredit.period_end > now)
    )
    usage = result.scalar_one_or_none()

    if usage is None:
        return {"credits_used": 0, "exceeded": False, "warning": False}

    usage.credits_used += amount
    await db.commit()
    await db.refresh(usage)

    # No limit (Pro/Cabinet) → never exceeded
    if usage.credits_total == 0:
        return {"credits_used": usage.credits_used, "exceeded": False, "warning": False}

    grace_limit = int(usage.credits_total * (1 + GRACE_OVERAGE_PCT))
    exceeded = usage.credits_used > grace_limit
    warning = usage.credits_used > usage.credits_total and not exceeded

    return {
        "credits_used": usage.credits_used,
        "credits_remaining": max(0, usage.credits_total - usage.credits_used),
        "exceeded": exceeded,
        "warning": warning,
    }


# ── Invoice retrieval ────────────────────────────────────────────

async def list_invoices(stripe_customer_id: str, limit: int = 12) -> list:
    """List recent invoices for a Stripe customer."""
    invoices = stripe.Invoice.list(customer=stripe_customer_id, limit=limit)
    return [
        {
            "id": inv.id,
            "number": inv.number,
            "date": datetime.fromtimestamp(inv.created, tz=timezone.utc).isoformat(),
            "amount_ht": inv.subtotal / 100,
            "amount_ttc": inv.total / 100,
            "currency": inv.currency,
            "status": inv.status,
            "pdf_url": inv.invoice_pdf,
            "hosted_url": inv.hosted_invoice_url,
        }
        for inv in invoices.data
    ]


# ── Payment method info ──────────────────────────────────────────

async def get_payment_method(stripe_customer_id: str) -> Optional[dict]:
    """Get the default payment method for a customer."""
    customer = stripe.Customer.retrieve(stripe_customer_id)
    pm_id = customer.get("invoice_settings", {}).get("default_payment_method")
    if not pm_id:
        return None

    pm = stripe.PaymentMethod.retrieve(pm_id)
    card = pm.get("card", {})
    return {
        "type": pm.type,
        "brand": card.get("brand"),
        "last4": card.get("last4"),
        "exp_month": card.get("exp_month"),
        "exp_year": card.get("exp_year"),
    }


# ── Billing event logging ────────────────────────────────────────

async def log_billing_event(
    db: AsyncSession,
    stripe_event_id: str,
    event_type: str,
    firm_id: Optional[str] = None,
    amount: Optional[float] = None,
    currency: str = "eur",
    status: str = "processed",
    metadata: Optional[dict] = None,
) -> BillingEvent:
    """Persist a billing event for audit trail."""
    event = BillingEvent(
        firm_id=firm_id,
        stripe_event_id=stripe_event_id,
        event_type=event_type,
        amount=amount,
        currency=currency,
        status=status,
        metadata_json=metadata,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
