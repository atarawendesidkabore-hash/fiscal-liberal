"""
Usage enforcement middleware — checks calculation limits before allowing requests.

Provides a FastAPI dependency that can be injected into calculation endpoints.
"""
import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.billing_models import FirmSubscription, UsageCredit
from fiscia.config.stripe_config import GRACE_OVERAGE_PCT
from fiscia.database_async import get_async_db
from fiscia.dependencies import CurrentUser, get_current_user

logger = logging.getLogger("fiscia.usage")


async def check_usage_limit(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> CurrentUser:
    """
    FastAPI dependency that enforces calculation limits.

    - No firm / no subscription → allow (v1 backward compat, no firm required)
    - Unlimited plan (Pro/Cabinet) → allow
    - Within limit → allow
    - 10% grace zone → allow with X-Usage-Warning header (logged)
    - Over grace limit → HTTP 402 Payment Required
    """
    if not user.firm_id:
        # No firm attached — legacy/unsubscribed user, allow through
        return user

    # Check subscription status
    result = await db.execute(
        select(FirmSubscription).where(
            FirmSubscription.firm_id == user.firm_id,
        )
    )
    sub = result.scalar_one_or_none()

    if sub is None:
        # No subscription record — allow (free tier / legacy)
        return user

    if sub.status not in ("active", "trialing"):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Abonnement inactif. Veuillez renouveler votre abonnement.",
        )

    # Get current usage
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UsageCredit)
        .where(UsageCredit.firm_id == user.firm_id)
        .where(UsageCredit.period_start <= now)
        .where(UsageCredit.period_end > now)
    )
    usage = result.scalar_one_or_none()

    if usage is None or usage.credits_total == 0:
        # No usage record or unlimited plan → allow
        return user

    grace_limit = int(usage.credits_total * (1 + GRACE_OVERAGE_PCT))

    if usage.credits_used >= grace_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Limite de calculs atteinte ({usage.credits_used}/{usage.credits_total}). "
                f"Passez au plan Pro pour des calculs illimites."
            ),
        )

    if usage.credits_used >= usage.credits_total:
        logger.warning(
            "Firm %s in grace period: %d/%d used (grace limit: %d)",
            user.firm_id, usage.credits_used, usage.credits_total, grace_limit,
        )

    return user


async def increment_usage(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """
    Increment usage counter after a successful calculation.

    Call this AFTER the calculation succeeds (not before),
    so failed calculations don't consume credits.
    """
    if not user.firm_id:
        return

    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UsageCredit)
        .where(UsageCredit.firm_id == user.firm_id)
        .where(UsageCredit.period_start <= now)
        .where(UsageCredit.period_end > now)
    )
    usage = result.scalar_one_or_none()

    if usage is None:
        return

    usage.credits_used += 1
    await db.commit()
