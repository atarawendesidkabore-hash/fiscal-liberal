"""
Stripe webhook handler — processes incoming Stripe events.

Verifies webhook signature, dispatches to event-specific handlers,
and persists billing events for audit trail.
"""
import logging
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.billing_models import BillingEvent, FirmSubscription, UsageCredit
from fiscia.config.stripe_config import (
    PLAN_METADATA,
    STRIPE_WEBHOOK_SECRET,
)
from fiscia.database_async import get_async_db
from fiscia.stripe_service import log_billing_event

logger = logging.getLogger("fiscia.webhooks.stripe")

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Stripe webhook endpoint. Verifies signature and dispatches events.

    Events handled:
    - invoice.payment_succeeded → renew subscription, reset usage
    - invoice.payment_failed → mark past_due, log failure
    - customer.subscription.updated → sync status changes
    - customer.subscription.deleted → revoke access
    - checkout.session.completed → activate new subscription
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    event_id = event["id"]
    data = event["data"]["object"]

    logger.info("Stripe webhook received: %s (%s)", event_type, event_id)

    # Idempotency: skip if we already processed this event
    existing = await db.execute(
        select(BillingEvent).where(BillingEvent.stripe_event_id == event_id)
    )
    if existing.scalar_one_or_none() is not None:
        logger.info("Duplicate event %s — skipping", event_id)
        return {"status": "duplicate", "event_id": event_id}

    # Dispatch to handler
    handler = HANDLERS.get(event_type)
    if handler:
        await handler(db, event_id, data)
    else:
        logger.debug("Unhandled event type: %s", event_type)

    return {"status": "ok", "event_id": event_id}


# ── Event handlers ───────────────────────────────────────────────

async def _handle_checkout_completed(db: AsyncSession, event_id: str, session: dict):
    """Activate subscription after successful checkout."""
    firm_id = session.get("metadata", {}).get("firm_id")
    plan_name = session.get("metadata", {}).get("plan", "starter")
    stripe_subscription_id = session.get("subscription")
    stripe_customer_id = session.get("customer")

    if not firm_id:
        logger.warning("Checkout completed without firm_id metadata")
        await log_billing_event(db, event_id, "checkout.session.completed", status="ignored")
        return

    # Update or create FirmSubscription
    result = await db.execute(
        select(FirmSubscription).where(FirmSubscription.firm_id == firm_id)
    )
    sub = result.scalar_one_or_none()

    if sub:
        sub.stripe_subscription_id = stripe_subscription_id
        sub.stripe_customer_id = stripe_customer_id or sub.stripe_customer_id
        sub.plan_id = plan_name
        sub.status = "active"
    else:
        sub = FirmSubscription(
            firm_id=firm_id,
            plan_id=plan_name,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            status="active",
        )
        db.add(sub)

    # Initialize usage credits for the period
    await _reset_usage_credits(db, firm_id, plan_name)

    await db.commit()
    await log_billing_event(
        db, event_id, "checkout.session.completed",
        firm_id=firm_id,
        metadata={"plan": plan_name, "subscription_id": stripe_subscription_id},
    )
    logger.info("Subscription activated for firm %s on plan %s", firm_id, plan_name)


async def _handle_invoice_succeeded(db: AsyncSession, event_id: str, invoice: dict):
    """Payment succeeded — renew subscription and reset usage credits."""
    customer_id = invoice.get("customer")
    amount = (invoice.get("amount_paid", 0)) / 100
    subscription_id = invoice.get("subscription")

    sub = await _find_subscription_by_customer(db, customer_id)
    if not sub:
        await log_billing_event(
            db, event_id, "invoice.payment_succeeded",
            amount=amount, status="no_subscription",
        )
        return

    # Ensure subscription is active
    sub.status = "active"

    # Reset usage credits for new period
    await _reset_usage_credits(db, sub.firm_id, sub.plan_id)

    await db.commit()
    await log_billing_event(
        db, event_id, "invoice.payment_succeeded",
        firm_id=sub.firm_id, amount=amount,
        metadata={"subscription_id": subscription_id},
    )
    logger.info("Invoice paid for firm %s: %.2f EUR", sub.firm_id, amount)


async def _handle_invoice_failed(db: AsyncSession, event_id: str, invoice: dict):
    """Payment failed — mark subscription as past_due."""
    customer_id = invoice.get("customer")
    amount = (invoice.get("amount_due", 0)) / 100
    attempt_count = invoice.get("attempt_count", 0)

    sub = await _find_subscription_by_customer(db, customer_id)
    if not sub:
        await log_billing_event(
            db, event_id, "invoice.payment_failed",
            amount=amount, status="no_subscription",
        )
        return

    sub.status = "past_due"
    await db.commit()

    await log_billing_event(
        db, event_id, "invoice.payment_failed",
        firm_id=sub.firm_id, amount=amount,
        metadata={"attempt_count": attempt_count, "subscription_id": sub.stripe_subscription_id},
    )
    logger.warning(
        "Payment failed for firm %s (attempt %d): %.2f EUR",
        sub.firm_id, attempt_count, amount,
    )


async def _handle_subscription_updated(db: AsyncSession, event_id: str, subscription: dict):
    """Subscription updated — sync status and period dates."""
    customer_id = subscription.get("customer")
    new_status = subscription.get("status", "active")
    plan_name = subscription.get("metadata", {}).get("plan")

    sub = await _find_subscription_by_customer(db, customer_id)
    if not sub:
        await log_billing_event(
            db, event_id, "customer.subscription.updated",
            status="no_subscription",
        )
        return

    sub.status = new_status
    sub.cancel_at_period_end = subscription.get("cancel_at_period_end", False)

    period_start = subscription.get("current_period_start")
    period_end = subscription.get("current_period_end")
    if period_start:
        sub.current_period_start = datetime.fromtimestamp(period_start, tz=timezone.utc)
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)
    if plan_name:
        sub.plan_id = plan_name

    await db.commit()
    await log_billing_event(
        db, event_id, "customer.subscription.updated",
        firm_id=sub.firm_id,
        metadata={"status": new_status, "cancel_at_period_end": sub.cancel_at_period_end},
    )


async def _handle_subscription_deleted(db: AsyncSession, event_id: str, subscription: dict):
    """Subscription canceled/expired — revoke access."""
    customer_id = subscription.get("customer")

    sub = await _find_subscription_by_customer(db, customer_id)
    if not sub:
        await log_billing_event(
            db, event_id, "customer.subscription.deleted",
            status="no_subscription",
        )
        return

    sub.status = "canceled"
    sub.stripe_subscription_id = None
    await db.commit()

    await log_billing_event(
        db, event_id, "customer.subscription.deleted",
        firm_id=sub.firm_id,
        metadata={"customer_id": customer_id},
    )
    logger.info("Subscription deleted for firm %s", sub.firm_id)


async def _handle_charge_succeeded(db: AsyncSession, event_id: str, charge: dict):
    """Individual charge succeeded — log for audit."""
    customer_id = charge.get("customer")
    amount = charge.get("amount", 0) / 100

    sub = await _find_subscription_by_customer(db, customer_id)
    firm_id = sub.firm_id if sub else None

    await log_billing_event(
        db, event_id, "charge.succeeded",
        firm_id=firm_id, amount=amount,
    )


async def _handle_charge_failed(db: AsyncSession, event_id: str, charge: dict):
    """Individual charge failed — log for audit."""
    customer_id = charge.get("customer")
    amount = charge.get("amount", 0) / 100
    failure_message = charge.get("failure_message", "Unknown")

    sub = await _find_subscription_by_customer(db, customer_id)
    firm_id = sub.firm_id if sub else None

    await log_billing_event(
        db, event_id, "charge.failed",
        firm_id=firm_id, amount=amount, status="failed",
        metadata={"failure_message": failure_message},
    )


# ── Helpers ──────────────────────────────────────────────────────

async def _find_subscription_by_customer(
    db: AsyncSession, customer_id: str
) -> FirmSubscription | None:
    """Look up FirmSubscription by Stripe customer ID."""
    if not customer_id:
        return None
    result = await db.execute(
        select(FirmSubscription).where(
            FirmSubscription.stripe_customer_id == customer_id
        )
    )
    return result.scalar_one_or_none()


async def _reset_usage_credits(db: AsyncSession, firm_id: str, plan_name: str):
    """Create or reset usage credits for the current billing period."""
    meta = PLAN_METADATA.get(plan_name, {})
    calc_limit = meta.get("calculation_limit", 0) or 0  # None → 0 (unlimited)

    now = datetime.now(timezone.utc)
    # Find current period end (roughly 30 days from now)
    from datetime import timedelta
    period_end = now + timedelta(days=30)

    # Check for existing current-period record
    result = await db.execute(
        select(UsageCredit)
        .where(UsageCredit.firm_id == firm_id)
        .where(UsageCredit.period_end > now)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.credits_total = calc_limit
        existing.credits_used = 0
        existing.period_start = now
        existing.period_end = period_end
    else:
        usage = UsageCredit(
            firm_id=firm_id,
            credits_total=calc_limit,
            credits_used=0,
            period_start=now,
            period_end=period_end,
        )
        db.add(usage)


# ── Event dispatch table ─────────────────────────────────────────

HANDLERS = {
    "checkout.session.completed": _handle_checkout_completed,
    "invoice.payment_succeeded": _handle_invoice_succeeded,
    "invoice.payment_failed": _handle_invoice_failed,
    "customer.subscription.updated": _handle_subscription_updated,
    "customer.subscription.deleted": _handle_subscription_deleted,
    "charge.succeeded": _handle_charge_succeeded,
    "charge.failed": _handle_charge_failed,
}
