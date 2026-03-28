"""
Billing API endpoints — subscription management, usage, invoices.

All endpoints under /billing prefix. Auth required except GET /billing/plans.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.billing_models import FirmSubscription
from fiscia.config.stripe_config import PLAN_METADATA
from fiscia.database_async import get_async_db
from fiscia.dependencies import CurrentUser, get_current_user, require_role
from fiscia.stripe_service import (
    cancel_subscription,
    create_billing_portal_session,
    create_checkout_session,
    create_customer,
    get_payment_method,
    get_usage_for_firm,
    list_invoices,
    update_subscription_plan,
)

logger = logging.getLogger("fiscia.billing")

router = APIRouter(prefix="/billing", tags=["billing"])


# ── Request schemas ──────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    plan: str = Field(..., pattern="^(starter|pro|cabinet)$", description="Plan name")
    trial: bool = Field(default=False, description="Start with 14-day free trial")


class ChangePlanRequest(BaseModel):
    new_plan: str = Field(..., pattern="^(starter|pro|cabinet)$", description="Target plan")


# ── GET /billing/plans — public pricing ──────────────────────────

@router.get("/plans")
async def list_plans():
    """List available subscription plans with pricing (public)."""
    plans = []
    for name, meta in PLAN_METADATA.items():
        plans.append({
            "name": name,
            "price_eur": meta["price_eur"],
            "price_annual_eur": round(meta["price_eur"] * 10, 2),
            "calculation_limit": meta["calculation_limit"],
            "user_limit": meta["user_limit"],
            "features": _plan_features(name),
        })
    return {"plans": plans}


# ── POST /billing/subscribe — create checkout session ────────────

@router.post("/subscribe")
async def subscribe(
    req: SubscribeRequest,
    user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """Create a Stripe Checkout Session for subscription. Admin only."""
    if not user.firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucun cabinet associe. Creez un cabinet d'abord.",
        )

    # Check for existing active subscription
    result = await db.execute(
        select(FirmSubscription).where(
            FirmSubscription.firm_id == user.firm_id,
            FirmSubscription.status.in_(["active", "trialing"]),
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un abonnement actif existe deja. Utilisez /billing/change-plan pour changer de formule.",
        )

    # Get or create Stripe customer
    result = await db.execute(
        select(FirmSubscription).where(FirmSubscription.firm_id == user.firm_id)
    )
    sub_record = result.scalar_one_or_none()

    if sub_record and sub_record.stripe_customer_id:
        stripe_customer_id = sub_record.stripe_customer_id
    else:
        stripe_customer_id = await create_customer(
            firm_name=f"Firm-{user.firm_id[:8]}",
            email=user.email,
            firm_id=user.firm_id,
        )
        # Persist the customer ID for later webhook matching
        new_sub = FirmSubscription(
            firm_id=user.firm_id,
            plan_id=req.plan,
            stripe_customer_id=stripe_customer_id,
            status="incomplete",
        )
        db.add(new_sub)
        await db.commit()

    checkout_url = await create_checkout_session(
        plan_name=req.plan,
        stripe_customer_id=stripe_customer_id,
        firm_id=user.firm_id,
        trial=req.trial,
    )
    return {"checkout_url": checkout_url}


# ── POST /billing/cancel — cancel subscription ──────────────────

@router.post("/cancel")
async def cancel(
    user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """Cancel subscription at end of current billing period. Admin only."""
    sub = await _get_active_subscription(db, user.firm_id)

    if not sub.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun abonnement Stripe actif.",
        )

    result = await cancel_subscription(sub.stripe_subscription_id)

    sub.cancel_at_period_end = True
    await db.commit()

    return {
        "message": "Abonnement programme pour annulation en fin de periode.",
        "cancel_at": result["current_period_end"],
    }


# ── POST /billing/change-plan — upgrade/downgrade ───────────────

@router.post("/change-plan")
async def change_plan(
    req: ChangePlanRequest,
    user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """Change subscription plan (prorated). Admin only."""
    sub = await _get_active_subscription(db, user.firm_id)

    if sub.plan_id == req.new_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vous etes deja sur le plan '{req.new_plan}'.",
        )

    if not sub.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun abonnement Stripe actif.",
        )

    result = await update_subscription_plan(sub.stripe_subscription_id, req.new_plan)

    sub.plan_id = req.new_plan
    await db.commit()

    return {
        "message": f"Plan change vers '{req.new_plan}' avec succes.",
        "new_plan": req.new_plan,
        "status": result["status"],
    }


# ── GET /billing/usage — current usage stats ────────────────────

@router.get("/usage")
async def usage(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get current billing period usage for the firm."""
    if not user.firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucun cabinet associe.",
        )

    usage_data = await get_usage_for_firm(db, user.firm_id)

    # Also include subscription info
    result = await db.execute(
        select(FirmSubscription).where(
            FirmSubscription.firm_id == user.firm_id,
            FirmSubscription.status.in_(["active", "trialing"]),
        )
    )
    sub = result.scalar_one_or_none()
    plan_name = sub.plan_id if sub else None

    return {
        "plan": plan_name,
        **usage_data,
    }


# ── GET /billing/invoices — invoice history ──────────────────────

@router.get("/invoices")
async def invoices(
    user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """List invoice history from Stripe. Admin only."""
    sub = await _get_active_subscription(db, user.firm_id)
    invoice_list = await list_invoices(sub.stripe_customer_id)
    return {"invoices": invoice_list}


# ── GET /billing/payment-method — card info ──────────────────────

@router.get("/payment-method")
async def payment_method(
    user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """Get current payment method details. Admin only."""
    sub = await _get_active_subscription(db, user.firm_id)
    pm = await get_payment_method(sub.stripe_customer_id)
    if pm is None:
        return {"payment_method": None, "message": "Aucun moyen de paiement enregistre."}
    return {"payment_method": pm}


# ── GET /billing/portal — Stripe billing portal ─────────────────

@router.get("/portal")
async def billing_portal(
    user: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """Generate a Stripe Billing Portal link for payment method management."""
    sub = await _get_active_subscription(db, user.firm_id)
    portal_url = await create_billing_portal_session(sub.stripe_customer_id)
    return {"portal_url": portal_url}


# ── Helpers ──────────────────────────────────────────────────────

async def _get_active_subscription(db: AsyncSession, firm_id: str) -> FirmSubscription:
    """Retrieve the active subscription for a firm or raise 404."""
    if not firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucun cabinet associe.",
        )
    result = await db.execute(
        select(FirmSubscription).where(FirmSubscription.firm_id == firm_id)
    )
    sub = result.scalar_one_or_none()
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun abonnement trouve pour ce cabinet.",
        )
    return sub


def _plan_features(name: str) -> list:
    """Return feature list for display."""
    base = ["Calcul IS Art. 219 CGI", "Liasse 2058-A automatisee", "Support email"]
    if name == "starter":
        return base + ["50 calculs/mois", "1 utilisateur"]
    elif name == "pro":
        return base + ["Calculs illimites", "1 utilisateur", "Assistant IA fiscal", "Support prioritaire (4h)"]
    else:
        return base + [
            "Calculs illimites", "Jusqu'a 10 utilisateurs",
            "IA avancee + modele local", "Support telephonique (1h)",
            "API access", "Multi-cabinet",
        ]
