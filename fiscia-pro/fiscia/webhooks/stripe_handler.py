from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.crud import CrudError, create_audit_log
from fiscia.dependencies import get_async_db_session
from fiscia.stripe_service import BillingError, StripeService, StripeWebhookError

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(default="", alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    payload = await request.body()

    try:
        event = StripeService.verify_webhook_signature(payload, stripe_signature)
        result = await StripeService.handle_webhook_event(session, event=event)
    except StripeWebhookError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    try:
        await create_audit_log(
            session=session,
            user_id=None,
            firm_id=result.get("firm_id"),
            action="stripe_webhook",
            resource_type="billing",
            resource_id=None,
            details={"event_id": result.get("event_id"), "event_type": result.get("event_type")},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except CrudError:
        pass

    return {"status": "ok", "result": result}