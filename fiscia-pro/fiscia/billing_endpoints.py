from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.auth_models import Role, User
from fiscia.crud import CrudError, create_audit_log
from fiscia.dependencies import get_async_db_session
from fiscia.rbac import require_role
from fiscia.stripe_service import BillingError, StripeService

router = APIRouter(prefix="/billing", tags=["billing"])


class SubscribeInput(BaseModel):
    plan_name: str = Field(..., min_length=2, max_length=32)
    success_url: str = Field(default="https://example.com/billing/success")
    cancel_url: str = Field(default="https://example.com/billing/cancel")


class CancelInput(BaseModel):
    at_period_end: bool = True


class UpgradeInput(BaseModel):
    plan_name: str = Field(..., min_length=2, max_length=32)


@router.get("/plans")
async def list_plans(session: AsyncSession = Depends(get_async_db_session)) -> dict:
    plans = await StripeService.get_public_plans(session)
    return {"plans": plans}


@router.post("/subscribe")
async def subscribe(
    payload: SubscribeInput,
    request: Request,
    current_user: User = Depends(require_role(Role.ADMIN.value)),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    try:
        checkout = await StripeService.create_checkout_session(
            session,
            firm_id=current_user.firm_id,
            email=current_user.email,
            plan_name=payload.plan_name,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
        )
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    try:
        await create_audit_log(
            session=session,
            user_id=current_user.id,
            firm_id=current_user.firm_id,
            action="billing_subscribe_checkout",
            resource_type="billing",
            resource_id=None,
            details={"plan_name": payload.plan_name, "checkout_session_id": checkout.get("checkout_session_id")},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except CrudError:
        pass

    return checkout


@router.post("/upgrade")
async def upgrade_plan(
    payload: UpgradeInput,
    request: Request,
    current_user: User = Depends(require_role(Role.ADMIN.value)),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    try:
        sub = await StripeService.upgrade_subscription(session, firm_id=current_user.firm_id, plan_name=payload.plan_name)
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    try:
        await create_audit_log(
            session=session,
            user_id=current_user.id,
            firm_id=current_user.firm_id,
            action="billing_upgrade",
            resource_type="billing",
            resource_id=sub.id,
            details={"plan_name": payload.plan_name, "stripe_subscription_id": sub.stripe_subscription_id},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except CrudError:
        pass

    return {
        "subscription_id": sub.id,
        "status": sub.status,
        "plan_id": sub.plan_id,
        "current_period_start": sub.current_period_start,
        "current_period_end": sub.current_period_end,
    }


@router.post("/cancel")
async def cancel_subscription(
    payload: CancelInput,
    request: Request,
    current_user: User = Depends(require_role(Role.ADMIN.value)),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    try:
        sub = await StripeService.cancel_subscription(
            session,
            firm_id=current_user.firm_id,
            at_period_end=payload.at_period_end,
        )
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    try:
        await create_audit_log(
            session=session,
            user_id=current_user.id,
            firm_id=current_user.firm_id,
            action="billing_cancel",
            resource_type="billing",
            resource_id=sub.id,
            details={"at_period_end": payload.at_period_end, "stripe_subscription_id": sub.stripe_subscription_id},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except CrudError:
        pass

    return {
        "subscription_id": sub.id,
        "status": sub.status,
        "cancel_at_period_end": payload.at_period_end,
        "current_period_end": sub.current_period_end,
    }


@router.get("/usage")
async def usage(
    current_user: User = Depends(require_role(Role.FISCALISTE.value)),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    summary = await StripeService.get_usage_summary(session, firm_id=current_user.firm_id)
    return {"usage": summary}


@router.get("/invoices")
async def invoices(
    current_user: User = Depends(require_role(Role.FISCALISTE.value)),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    rows = await StripeService.list_invoices(session, firm_id=current_user.firm_id)
    return {"invoices": rows}
