from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.auth_models import Firm
from fiscia.billing_models import BillingEvent, FirmSubscription, SubscriptionPlan, UsageCredit


class BillingError(RuntimeError):
    pass


class StripeWebhookError(BillingError):
    pass


class InsufficientCreditsError(BillingError):
    pass


class StripeService:
    STRIPE_API_BASE = os.getenv("STRIPE_API_BASE", "https://api.stripe.com/v1")
    WEBHOOK_TOLERANCE_SECONDS = int(os.getenv("STRIPE_WEBHOOK_TOLERANCE_SECONDS", "300"))
    DEFAULT_CURRENCY = os.getenv("BILLING_CURRENCY", "eur").strip().lower()
    DEFAULT_LOCALE = os.getenv("BILLING_LOCALE", "fr").strip().lower()
    RECEIPT_FOOTER_FR = os.getenv(
        "STRIPE_RECEIPT_FOOTER_FR",
        "Merci de votre confiance. Facturation FiscIA Pro - Support: support@fiscia.pro",
    )
    SUPPORTED_PAYMENT_METHODS = ("card", "sepa_debit")
    SUPPORTED_WALLETS = ("apple_pay", "google_pay")

    PLAN_DEFINITIONS: dict[str, dict[str, Any]] = {
        "starter": {
            "name": "starter",
            "price": Decimal("29.00"),
            "calculation_limit": 50,
            "stripe_price_id": os.getenv("STRIPE_PRICE_STARTER", "price_starter_monthly"),
        },
        "pro": {
            "name": "pro",
            "price": Decimal("79.00"),
            "calculation_limit": -1,
            "stripe_price_id": os.getenv("STRIPE_PRICE_PRO", "price_pro_monthly"),
        },
        "cabinet": {
            "name": "cabinet",
            "price": Decimal("199.00"),
            "calculation_limit": -1,
            "stripe_price_id": os.getenv("STRIPE_PRICE_CABINET", "price_cabinet_monthly"),
        },
    }

    @classmethod
    def _now(cls) -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def _current_period(cls) -> str:
        return cls._now().strftime("%Y-%m")

    @classmethod
    def _period_from_epoch(cls, epoch: int | None) -> str:
        if not epoch:
            return cls._current_period()
        return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m")

    @staticmethod
    def _easter_sunday(year: int) -> date:
        # Meeus/Jones/Butcher algorithm.
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)

    @classmethod
    def _french_bank_holidays(cls, year: int) -> set[date]:
        easter = cls._easter_sunday(year)
        return {
            date(year, 1, 1),   # Jour de l'an
            date(year, 5, 1),   # Fete du travail
            date(year, 5, 8),   # Victoire 1945
            date(year, 7, 14),  # Fete nationale
            date(year, 8, 15),  # Assomption
            date(year, 11, 1),  # Toussaint
            date(year, 11, 11), # Armistice
            date(year, 12, 25), # Noel
            easter + timedelta(days=1),   # Lundi de Paques
            easter + timedelta(days=39),  # Ascension
            easter + timedelta(days=50),  # Lundi de Pentecote
        }

    @classmethod
    def is_french_bank_holiday(cls, target: date) -> bool:
        return target in cls._french_bank_holidays(target.year)

    @classmethod
    def is_french_business_day(cls, target: date) -> bool:
        return target.weekday() < 5 and not cls.is_french_bank_holiday(target)

    @classmethod
    def next_french_business_day(cls, target: date) -> date:
        current = target
        while not cls.is_french_business_day(current):
            current += timedelta(days=1)
        return current

    @classmethod
    def next_collection_business_day(cls, *, from_dt: datetime | None = None) -> date:
        anchor = (from_dt or cls._now()).date() + timedelta(days=1)
        return cls.next_french_business_day(anchor)

    @classmethod
    async def _commit(cls, session: AsyncSession) -> None:
        try:
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

    @classmethod
    def _stripe_secret_key(cls) -> str:
        key = os.getenv("STRIPE_SECRET_KEY")
        if not key:
            raise BillingError("STRIPE_SECRET_KEY is not configured.")
        return key

    @classmethod
    def _webhook_secret(cls) -> str:
        secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not secret:
            raise StripeWebhookError("STRIPE_WEBHOOK_SECRET is not configured.")
        return secret

    @classmethod
    async def _stripe_request(
        cls,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{cls.STRIPE_API_BASE.rstrip('/')}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.request(
                method.upper(),
                url,
                auth=(cls._stripe_secret_key(), ""),
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {"detail": response.text}
            raise BillingError(f"Stripe API error ({response.status_code}): {payload}")

        if not response.text.strip():
            return {}

        try:
            return response.json()
        except ValueError as exc:
            raise BillingError("Stripe response is not valid JSON.") from exc

    @classmethod
    async def seed_subscription_plans(cls, session: AsyncSession) -> None:
        for key, plan in cls.PLAN_DEFINITIONS.items():
            res = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == key))
            row = res.scalar_one_or_none()
            if row is None:
                row = SubscriptionPlan(
                    name=plan["name"],
                    stripe_price_id=plan["stripe_price_id"],
                    price=plan["price"],
                    calculation_limit=plan["calculation_limit"],
                )
                session.add(row)
            else:
                row.stripe_price_id = plan["stripe_price_id"]
                row.price = plan["price"]
                row.calculation_limit = plan["calculation_limit"]
        await cls._commit(session)

    @classmethod
    async def get_public_plans(cls, session: AsyncSession) -> list[dict[str, Any]]:
        await cls.seed_subscription_plans(session)
        res = await session.execute(select(SubscriptionPlan).order_by(SubscriptionPlan.price.asc()))
        plans = list(res.scalars().all())
        return [
            {
                "name": p.name,
                "price": float(p.price),
                "calculation_limit": p.calculation_limit,
                "unlimited": p.calculation_limit < 0,
            }
            for p in plans
        ]

    @classmethod
    async def _get_firm(cls, session: AsyncSession, firm_id: int) -> Firm:
        res = await session.execute(select(Firm).where(Firm.id == firm_id))
        firm = res.scalar_one_or_none()
        if firm is None:
            raise BillingError("Firm not found.")
        return firm

    @classmethod
    async def _get_plan_by_name(cls, session: AsyncSession, plan_name: str) -> SubscriptionPlan:
        await cls.seed_subscription_plans(session)
        normalized = plan_name.strip().lower()
        res = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == normalized))
        plan = res.scalar_one_or_none()
        if plan is None:
            raise BillingError(f"Unknown plan: {plan_name}")
        return plan

    @classmethod
    async def _get_plan_by_price_id(cls, session: AsyncSession, price_id: str | None) -> SubscriptionPlan | None:
        if not price_id:
            return None
        await cls.seed_subscription_plans(session)
        res = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.stripe_price_id == price_id))
        return res.scalar_one_or_none()

    @classmethod
    async def _get_subscription_by_firm(cls, session: AsyncSession, firm_id: int) -> FirmSubscription | None:
        res = await session.execute(select(FirmSubscription).where(FirmSubscription.firm_id == firm_id))
        return res.scalar_one_or_none()

    @classmethod
    async def _get_subscription_by_customer(cls, session: AsyncSession, customer_id: str) -> FirmSubscription | None:
        res = await session.execute(select(FirmSubscription).where(FirmSubscription.stripe_customer_id == customer_id))
        return res.scalar_one_or_none()

    @classmethod
    async def _get_subscription_by_stripe_id(cls, session: AsyncSession, stripe_subscription_id: str) -> FirmSubscription | None:
        res = await session.execute(
            select(FirmSubscription).where(FirmSubscription.stripe_subscription_id == stripe_subscription_id)
        )
        return res.scalar_one_or_none()

    @classmethod
    async def create_or_update_customer(cls, session: AsyncSession, *, firm_id: int, email: str) -> str:
        payload = {
            "email": email,
            "metadata[firm_id]": str(firm_id),
            "metadata[billing_currency]": cls.DEFAULT_CURRENCY,
            "metadata[billing_locale]": cls.DEFAULT_LOCALE,
            "preferred_locales[0]": cls.DEFAULT_LOCALE,
            "invoice_settings[footer]": cls.RECEIPT_FOOTER_FR,
        }

        sub = await cls._get_subscription_by_firm(session, firm_id)
        if sub and sub.stripe_customer_id:
            await cls._stripe_request(
                "POST",
                f"customers/{sub.stripe_customer_id}",
                data=payload,
            )
            return sub.stripe_customer_id

        customer = await cls._stripe_request(
            "POST",
            "customers",
            data=payload,
        )
        customer_id = customer.get("id")
        if not customer_id:
            raise BillingError("Stripe customer id missing.")
        return str(customer_id)

    @classmethod
    async def create_checkout_session(
        cls,
        session: AsyncSession,
        *,
        firm_id: int,
        email: str,
        plan_name: str,
        success_url: str,
        cancel_url: str,
    ) -> dict[str, Any]:
        plan = await cls._get_plan_by_name(session, plan_name)
        customer_id = await cls.create_or_update_customer(session, firm_id=firm_id, email=email)
        first_collection_day = cls.next_collection_business_day()

        checkout = await cls._stripe_request(
            "POST",
            "checkout/sessions",
            data={
                "mode": "subscription",
                "customer": customer_id,
                "line_items[0][price]": plan.stripe_price_id,
                "line_items[0][quantity]": "1",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata[firm_id]": str(firm_id),
                "metadata[plan_name]": plan.name,
                "metadata[currency]": cls.DEFAULT_CURRENCY,
                "metadata[payment_profile]": "fr_optimized",
                "locale": cls.DEFAULT_LOCALE,
                "payment_method_collection": "always",
                "payment_method_types[0]": cls.SUPPORTED_PAYMENT_METHODS[0],
                "payment_method_types[1]": cls.SUPPORTED_PAYMENT_METHODS[1],
                "subscription_data[metadata][firm_id]": str(firm_id),
                "subscription_data[metadata][plan_name]": plan.name,
                "subscription_data[metadata][expected_collection_date]": first_collection_day.isoformat(),
                "subscription_data[metadata][currency]": cls.DEFAULT_CURRENCY,
            },
        )

        return {
            "checkout_session_id": checkout.get("id"),
            "checkout_url": checkout.get("url"),
            "stripe_customer_id": customer_id,
            "plan": plan.name,
            "currency": cls.DEFAULT_CURRENCY,
            "payment_methods": list(cls.SUPPORTED_PAYMENT_METHODS),
            "wallets_enabled": list(cls.SUPPORTED_WALLETS),
            "next_collection_business_day": first_collection_day.isoformat(),
            "locale": cls.DEFAULT_LOCALE,
        }

    @classmethod
    async def upgrade_subscription(cls, session: AsyncSession, *, firm_id: int, plan_name: str) -> FirmSubscription:
        subscription = await cls._get_subscription_by_firm(session, firm_id)
        if subscription is None:
            raise BillingError("No subscription for firm.")

        plan = await cls._get_plan_by_name(session, plan_name)
        remote_sub = await cls._stripe_request("GET", f"subscriptions/{subscription.stripe_subscription_id}")
        items = remote_sub.get("items", {}).get("data", [])
        if not items:
            raise BillingError("Stripe subscription has no item.")

        item_id = items[0].get("id")
        if not item_id:
            raise BillingError("Missing stripe subscription item id.")

        payload = await cls._stripe_request(
            "POST",
            f"subscriptions/{subscription.stripe_subscription_id}",
            data={
                "items[0][id]": item_id,
                "items[0][price]": plan.stripe_price_id,
                "proration_behavior": "create_prorations",
            },
        )

        subscription.plan_id = plan.id
        subscription.status = payload.get("status", subscription.status)
        if payload.get("current_period_start"):
            subscription.current_period_start = datetime.fromtimestamp(payload["current_period_start"], tz=timezone.utc)
        if payload.get("current_period_end"):
            subscription.current_period_end = datetime.fromtimestamp(payload["current_period_end"], tz=timezone.utc)
        subscription.updated_at = cls._now()

        firm = await cls._get_firm(session, firm_id)
        firm.plan_type = plan.name

        await cls._commit(session)
        await session.refresh(subscription)
        return subscription

    @classmethod
    async def cancel_subscription(cls, session: AsyncSession, *, firm_id: int, at_period_end: bool = True) -> FirmSubscription:
        subscription = await cls._get_subscription_by_firm(session, firm_id)
        if subscription is None:
            raise BillingError("No subscription for firm.")

        if at_period_end:
            payload = await cls._stripe_request(
                "POST",
                f"subscriptions/{subscription.stripe_subscription_id}",
                data={"cancel_at_period_end": "true"},
            )
        else:
            payload = await cls._stripe_request("DELETE", f"subscriptions/{subscription.stripe_subscription_id}")

        subscription.status = payload.get("status", "canceled")
        if payload.get("current_period_start"):
            subscription.current_period_start = datetime.fromtimestamp(payload["current_period_start"], tz=timezone.utc)
        if payload.get("current_period_end"):
            subscription.current_period_end = datetime.fromtimestamp(payload["current_period_end"], tz=timezone.utc)
        subscription.updated_at = cls._now()

        await cls._commit(session)
        await session.refresh(subscription)
        return subscription

    @classmethod
    async def _ensure_usage_row(cls, session: AsyncSession, *, firm_id: int) -> UsageCredit:
        period = cls._current_period()
        res = await session.execute(select(UsageCredit).where(UsageCredit.firm_id == firm_id, UsageCredit.period == period))
        usage = res.scalar_one_or_none()
        if usage is not None:
            return usage

        firm = await cls._get_firm(session, firm_id)
        plan = await cls._get_plan_by_name(session, firm.plan_type)
        usage = UsageCredit(firm_id=firm_id, credits_total=plan.calculation_limit, credits_used=0, period=period)
        session.add(usage)
        await cls._commit(session)
        await session.refresh(usage)
        return usage

    @classmethod
    async def ensure_usage_period(cls, session: AsyncSession, *, firm_id: int) -> UsageCredit:
        # Backward-compatible public name used by tests and callers.
        return await cls._ensure_usage_row(session, firm_id=firm_id)

    @classmethod
    async def allocate_usage_credits(cls, session: AsyncSession, *, firm_id: int, period: str, credits_total: int) -> UsageCredit:
        res = await session.execute(select(UsageCredit).where(UsageCredit.firm_id == firm_id, UsageCredit.period == period))
        usage = res.scalar_one_or_none()
        if usage is None:
            usage = UsageCredit(firm_id=firm_id, credits_total=credits_total, credits_used=0, period=period)
            session.add(usage)
        else:
            usage.credits_total = credits_total
            usage.credits_used = 0
        await cls._commit(session)
        await session.refresh(usage)
        return usage

    @classmethod
    async def consume_calculation_credit(
        cls,
        session: AsyncSession,
        *,
        firm_id: int,
        credits: int = 1,
        grace_limit: int = 0,
    ) -> dict[str, Any]:
        if credits <= 0:
            raise BillingError("credits must be positive")

        usage = await cls._ensure_usage_row(session, firm_id=firm_id)

        if usage.credits_total < 0:
            usage.credits_used += credits
            await cls._commit(session)
            await session.refresh(usage)
            return {
                "period": usage.period,
                "credits_total": usage.credits_total,
                "credits_used": usage.credits_used,
                "credits_remaining": -1,
                "overage_count": 0,
                "unlimited": True,
            }

        allowed = usage.credits_total + max(grace_limit, 0)
        next_used = usage.credits_used + credits
        if next_used > allowed:
            raise InsufficientCreditsError("Calculation quota exceeded for current period.")

        usage.credits_used = next_used
        await cls._commit(session)
        await session.refresh(usage)

        return {
            "period": usage.period,
            "credits_total": usage.credits_total,
            "credits_used": usage.credits_used,
            "credits_remaining": max(usage.credits_total - usage.credits_used, 0),
            "overage_count": max(usage.credits_used - usage.credits_total, 0),
            "unlimited": False,
        }

    @classmethod
    async def get_usage_summary(cls, session: AsyncSession, *, firm_id: int) -> dict[str, Any]:
        usage = await cls._ensure_usage_row(session, firm_id=firm_id)
        unlimited = usage.credits_total < 0
        return {
            "firm_id": firm_id,
            "period": usage.period,
            "credits_total": usage.credits_total,
            "credits_used": usage.credits_used,
            "credits_remaining": -1 if unlimited else max(usage.credits_total - usage.credits_used, 0),
            "overage_count": 0 if unlimited else max(usage.credits_used - usage.credits_total, 0),
            "unlimited": unlimited,
        }

    @classmethod
    async def record_billing_event(
        cls,
        session: AsyncSession,
        *,
        stripe_event_id: str,
        firm_id: int | None,
        event_type: str,
        amount: Decimal,
        status: str,
    ) -> BillingEvent:
        res = await session.execute(select(BillingEvent).where(BillingEvent.stripe_event_id == stripe_event_id))
        row = res.scalar_one_or_none()
        if row is not None:
            return row

        row = BillingEvent(
            stripe_event_id=stripe_event_id,
            firm_id=firm_id,
            type=event_type,
            amount=amount,
            status=status,
        )
        session.add(row)
        await cls._commit(session)
        await session.refresh(row)
        return row

    @classmethod
    async def list_invoices(cls, session: AsyncSession, *, firm_id: int, limit: int = 50) -> list[dict[str, Any]]:
        res = await session.execute(
            select(BillingEvent)
            .where(BillingEvent.firm_id == firm_id)
            .where(BillingEvent.type.like("invoice.%"))
            .order_by(BillingEvent.created_at.desc())
            .limit(limit)
        )
        rows = list(res.scalars().all())
        return [
            {
                "stripe_event_id": row.stripe_event_id,
                "type": row.type,
                "amount": float(row.amount),
                "status": row.status,
                "created_at": row.created_at,
                "currency": cls.DEFAULT_CURRENCY,
                "scheduled_collection_business_day": cls.next_french_business_day(row.created_at.date()).isoformat(),
            }
            for row in rows
        ]

    @classmethod
    def verify_webhook_signature(cls, payload: bytes, stripe_signature: str) -> dict[str, Any]:
        if not stripe_signature:
            raise StripeWebhookError("Missing Stripe-Signature header.")

        timestamp: str | None = None
        signatures: list[str] = []
        for part in stripe_signature.split(","):
            key, _, value = part.partition("=")
            if key == "t":
                timestamp = value
            elif key == "v1":
                signatures.append(value)

        if not timestamp or not signatures:
            raise StripeWebhookError("Invalid Stripe-Signature format.")

        try:
            ts = int(timestamp)
        except ValueError as exc:
            raise StripeWebhookError("Invalid Stripe-Signature timestamp.") from exc

        if abs(int(cls._now().timestamp()) - ts) > cls.WEBHOOK_TOLERANCE_SECONDS:
            raise StripeWebhookError("Webhook timestamp outside tolerance.")

        signed_payload = f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8")
        expected = hmac.new(cls._webhook_secret().encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        if not any(hmac.compare_digest(expected, candidate) for candidate in signatures):
            raise StripeWebhookError("Invalid webhook signature.")

        try:
            return json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise StripeWebhookError("Invalid webhook payload.") from exc

    @classmethod
    async def handle_webhook_event(cls, session: AsyncSession, *, event: dict[str, Any]) -> dict[str, Any]:
        event_id = event.get("id")
        event_type = event.get("type", "unknown")
        obj = event.get("data", {}).get("object", {})

        if not event_id:
            raise StripeWebhookError("Missing event id")

        existing = await session.execute(select(BillingEvent).where(BillingEvent.stripe_event_id == event_id))
        if existing.scalar_one_or_none() is not None:
            return {"processed": False, "reason": "duplicate", "event_id": event_id}

        customer_id = obj.get("customer")
        stripe_sub_id = obj.get("subscription") or obj.get("id")
        amount_minor = obj.get("amount_paid") or obj.get("amount_due") or obj.get("amount_total") or 0
        amount = (Decimal(str(amount_minor)) / Decimal("100")).quantize(Decimal("0.01"))

        subscription = None
        if customer_id:
            subscription = await cls._get_subscription_by_customer(session, str(customer_id))
        if subscription is None and stripe_sub_id:
            subscription = await cls._get_subscription_by_stripe_id(session, str(stripe_sub_id))

        firm_id = subscription.firm_id if subscription else None

        if event_type == "invoice.payment_succeeded" and subscription is not None:
            subscription.status = "active"
            if obj.get("current_period_start"):
                subscription.current_period_start = datetime.fromtimestamp(obj["current_period_start"], tz=timezone.utc)
            if obj.get("current_period_end"):
                subscription.current_period_end = datetime.fromtimestamp(obj["current_period_end"], tz=timezone.utc)

            plan = await session.get(SubscriptionPlan, subscription.plan_id)
            credits_total = plan.calculation_limit if plan else -1
            period = cls._period_from_epoch(obj.get("period_start") or obj.get("current_period_start"))
            await cls.allocate_usage_credits(session, firm_id=subscription.firm_id, period=period, credits_total=credits_total)

        elif event_type == "customer.subscription.deleted" and subscription is not None:
            subscription.status = "canceled"
            subscription.updated_at = cls._now()
            await cls._commit(session)

        elif event_type == "invoice.payment_failed" and subscription is not None:
            subscription.status = "past_due"
            subscription.updated_at = cls._now()
            await cls._commit(session)

        if event_type.startswith("customer.subscription.") and subscription is not None:
            items = obj.get("items", {}).get("data", [])
            price_id = items[0].get("price", {}).get("id") if items else None
            plan = await cls._get_plan_by_price_id(session, price_id)
            if plan is not None:
                subscription.plan_id = plan.id
                firm = await cls._get_firm(session, subscription.firm_id)
                firm.plan_type = plan.name

            subscription.status = obj.get("status", subscription.status)
            if obj.get("current_period_start"):
                subscription.current_period_start = datetime.fromtimestamp(obj["current_period_start"], tz=timezone.utc)
            if obj.get("current_period_end"):
                subscription.current_period_end = datetime.fromtimestamp(obj["current_period_end"], tz=timezone.utc)
            subscription.updated_at = cls._now()
            await cls._commit(session)

        status = "received"
        if event_type == "invoice.payment_succeeded":
            status = "succeeded"
        elif event_type == "invoice.payment_failed":
            status = "failed"

        await cls.record_billing_event(
            session,
            stripe_event_id=event_id,
            firm_id=firm_id,
            event_type=event_type,
            amount=amount,
            status=status,
        )

        next_collection_day = None
        if subscription is not None and subscription.current_period_end is not None:
            next_collection_day = cls.next_french_business_day(subscription.current_period_end.date()).isoformat()

        return {
            "processed": True,
            "event_id": event_id,
            "event_type": event_type,
            "firm_id": firm_id,
            "next_collection_business_day": next_collection_day,
            "currency": cls.DEFAULT_CURRENCY,
        }

    @classmethod
    def billing_health(cls) -> dict[str, Any]:
        return {
            "configured": bool(os.getenv("STRIPE_SECRET_KEY") and os.getenv("STRIPE_WEBHOOK_SECRET")),
            "webhook_endpoint": "/webhooks/stripe",
            "currency": cls.DEFAULT_CURRENCY,
            "locale": cls.DEFAULT_LOCALE,
            "payment_methods": list(cls.SUPPORTED_PAYMENT_METHODS),
            "wallets_enabled": list(cls.SUPPORTED_WALLETS),
            "holiday_calendar": "france_metropolitan",
            "plans": {
                key: {
                    "price": str(value["price"]),
                    "calculation_limit": value["calculation_limit"],
                    "stripe_price_id": value["stripe_price_id"],
                }
                for key, value in cls.PLAN_DEFINITIONS.items()
            },
        }
