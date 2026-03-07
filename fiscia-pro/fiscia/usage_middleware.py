from __future__ import annotations

from dataclasses import dataclass
import os

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.auth_models import User
from fiscia.dependencies import get_async_db_session
from fiscia.rbac import require_role
from fiscia.stripe_service import BillingError, InsufficientCreditsError, StripeService


@dataclass(slots=True)
class UsageGate:
    user: User
    usage: dict


def _grace_limit() -> int:
    try:
        return max(int(os.getenv("BILLING_GRACE_CALCULATIONS", "0")), 0)
    except ValueError:
        return 0


async def check_usage_credits(
    current_user: User = Depends(require_role("fiscaliste")),
    session: AsyncSession = Depends(get_async_db_session),
) -> UsageGate:
    try:
        usage = await StripeService.consume_calculation_credit(
            session,
            firm_id=current_user.firm_id,
            credits=1,
            grace_limit=_grace_limit(),
        )
    except InsufficientCreditsError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc)) from exc
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return UsageGate(user=current_user, usage=usage)