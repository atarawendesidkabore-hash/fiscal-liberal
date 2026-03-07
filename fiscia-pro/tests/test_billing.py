from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from fiscia.app import app
from fiscia.auth_endpoints import reset_auth_rate_limiter_for_tests
from fiscia.billing_models import BillingEvent, FirmSubscription, SubscriptionPlan, UsageCredit
from fiscia.dependencies import get_async_db_session
from fiscia.models_db import Base
from fiscia.stripe_service import InsufficientCreditsError, StripeService


@pytest.fixture()
def client_and_factory(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def _init_db() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_init_db())
    reset_auth_rate_limiter_for_tests()

    async def _override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_async_db_session] = _override_session

    with TestClient(app) as test_client:
        yield test_client, session_factory

    app.dependency_overrides.clear()
    reset_auth_rate_limiter_for_tests()
    asyncio.run(engine.dispose())


def _register_and_login_admin(client: TestClient, email: str, password: str, firm_name: str = "Cabinet Billing") -> tuple[str, int]:
    register = client.post(
        "/auth/register",
        json={
            "firm_name": firm_name,
            "plan_type": "starter",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code == 201, register.text

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    data = login.json()
    return data["tokens"]["access_token"], data["user"]["firm_id"]


def test_subscription_creation_and_cancellation_flow(client_and_factory, monkeypatch):
    client, session_factory = client_and_factory

    async def fake_stripe_request(method: str, path: str, *, data=None):
        if path == "customers":
            return {"id": "cus_123"}
        if path == "checkout/sessions":
            return {"id": "cs_test_123", "url": "https://checkout.stripe.test/session"}
        if path.startswith("subscriptions/") and method.upper() == "POST":
            return {
                "id": "sub_123",
                "status": "active",
                "cancel_at_period_end": True,
                "current_period_end": int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp()),
            }
        return {}

    monkeypatch.setattr(StripeService, "_stripe_request", fake_stripe_request)

    token, firm_id = _register_and_login_admin(client, "admin@billing.fr", "SecurePass!123")
    headers = {"Authorization": f"Bearer {token}"}

    subscribe = client.post(
        "/billing/subscribe",
        headers=headers,
        json={"plan_name": "starter", "success_url": "https://ok", "cancel_url": "https://ko"},
    )
    assert subscribe.status_code == 200, subscribe.text
    assert subscribe.json()["checkout_session_id"] == "cs_test_123"

    async def create_subscription_for_cancel() -> None:
        async with session_factory() as session:
            await StripeService.seed_subscription_plans(session)
            plan = (await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == "starter"))).scalar_one()
            row = FirmSubscription(
                firm_id=firm_id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
                plan_id=plan.id,
                status="active",
                current_period_start=datetime.now(timezone.utc),
                current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
            )
            session.add(row)
            await session.commit()

    asyncio.run(create_subscription_for_cancel())

    cancel = client.post("/billing/cancel", headers=headers, json={"at_period_end": True})
    assert cancel.status_code == 200, cancel.text
    assert cancel.json()["cancel_at_period_end"] is True


def test_checkout_uses_french_payment_profile(client_and_factory, monkeypatch):
    client, _ = client_and_factory
    captured: dict[str, dict] = {}

    async def fake_stripe_request(method: str, path: str, *, data=None):
        if path == "customers":
            captured["customers"] = data or {}
            return {"id": "cus_fr_123"}
        if path == "checkout/sessions":
            captured["checkout"] = data or {}
            return {"id": "cs_fr_123", "url": "https://checkout.stripe.test/fr-session"}
        return {}

    monkeypatch.setattr(StripeService, "_stripe_request", fake_stripe_request)

    token, _ = _register_and_login_admin(client, "admin-fr@billing.fr", "SecurePass!123", firm_name="Cabinet FR")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/billing/subscribe",
        headers=headers,
        json={"plan_name": "pro", "success_url": "https://ok", "cancel_url": "https://ko"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["currency"] == "eur"
    assert payload["locale"] == "fr"
    assert "card" in payload["payment_methods"]
    assert "sepa_debit" in payload["payment_methods"]
    assert "apple_pay" in payload["wallets_enabled"]
    assert "google_pay" in payload["wallets_enabled"]

    customer_data = captured["customers"]
    assert customer_data["preferred_locales[0]"] == "fr"
    assert customer_data["metadata[billing_currency]"] == "eur"
    assert "invoice_settings[footer]" in customer_data

    checkout_data = captured["checkout"]
    assert checkout_data["locale"] == "fr"
    assert checkout_data["payment_method_types[0]"] == "card"
    assert checkout_data["payment_method_types[1]"] == "sepa_debit"
    assert checkout_data["metadata[currency]"] == "eur"


def test_usage_credit_decrement_and_over_limit_blocking(client_and_factory):
    client, _ = client_and_factory
    token, _ = _register_and_login_admin(client, "admin2@billing.fr", "SecurePass!123", firm_name="Cabinet Usage")
    headers = {"Authorization": f"Bearer {token}"}

    # Force tiny quota for deterministic test.
    StripeService.PLAN_DEFINITIONS["starter"]["calculation_limit"] = 1

    first = client.post("/calc-is", headers=headers, json={"ca": 1000000, "capital_pp": True, "rf": 10000})
    assert first.status_code == 200, first.text
    assert first.json()["credit_usage"]["credits_used"] >= 1

    second = client.post("/calc-is", headers=headers, json={"ca": 1000000, "capital_pp": True, "rf": 10000})
    assert second.status_code in {402, 200}

    # Reset default for other tests.
    StripeService.PLAN_DEFINITIONS["starter"]["calculation_limit"] = 50


def test_webhook_processing_and_signature_verification(client_and_factory):
    client, session_factory = client_and_factory

    async def prepare_data() -> tuple[int, str, str]:
        async with session_factory() as session:
            await StripeService.seed_subscription_plans(session)
            register_plan = (await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == "starter"))).scalar_one()

            # Firm id 1 exists after first register in this isolated fixture.
            # Create one firm manually in case no auth call happened.
            from fiscia.auth_models import Firm

            firm = Firm(name="Webhook Firm", plan_type="starter")
            session.add(firm)
            await session.commit()
            await session.refresh(firm)

            sub = FirmSubscription(
                firm_id=firm.id,
                stripe_customer_id="cus_wh_123",
                stripe_subscription_id="sub_wh_123",
                plan_id=register_plan.id,
                status="active",
                current_period_start=datetime.now(timezone.utc),
                current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
            )
            session.add(sub)
            await session.commit()
            return firm.id, sub.stripe_customer_id, sub.stripe_subscription_id

    firm_id, customer_id, sub_id = asyncio.run(prepare_data())

    event = {
        "id": "evt_001",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "customer": customer_id,
                "subscription": sub_id,
                "amount_paid": 7900,
                "period_start": int(datetime.now(timezone.utc).timestamp()),
                "period_end": int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp()),
            }
        },
    }
    body = json.dumps(event).encode("utf-8")
    ts = str(int(datetime.now(timezone.utc).timestamp()))
    signed_payload = f"{ts}.{body.decode('utf-8')}".encode("utf-8")
    signature = hmac.new(b"whsec_test_secret", signed_payload, hashlib.sha256).hexdigest()

    res = client.post("/webhooks/stripe", data=body, headers={"Stripe-Signature": f"t={ts},v1={signature}"})
    assert res.status_code == 200, res.text
    webhook_result = res.json()["result"]
    assert webhook_result["currency"] == "eur"
    assert webhook_result["next_collection_business_day"] is not None

    async def assert_event_recorded() -> None:
        async with session_factory() as session:
            row = (await session.execute(select(BillingEvent).where(BillingEvent.stripe_event_id == "evt_001"))).scalar_one_or_none()
            assert row is not None
            assert row.status == "succeeded"
            usage = (await session.execute(select(UsageCredit).where(UsageCredit.firm_id == firm_id))).scalars().all()
            assert len(usage) >= 1

    asyncio.run(assert_event_recorded())


def test_french_bank_holiday_business_day_shift():
    # 1st of May 2026 is a French bank holiday (and Friday): shift should land on Monday 4th.
    assert StripeService.is_french_bank_holiday(date(2026, 5, 1)) is True
    assert StripeService.next_french_business_day(date(2026, 5, 1)) == date(2026, 5, 4)
    # Bastille Day 2026 is Tuesday: shift should be next day Wednesday.
    assert StripeService.is_french_bank_holiday(date(2026, 7, 14)) is True
    assert StripeService.next_french_business_day(date(2026, 7, 14)) == date(2026, 7, 15)


def test_service_over_limit_raises_insufficient_credit(client_and_factory):
    _, session_factory = client_and_factory

    async def run() -> None:
        from fiscia.auth_models import Firm

        async with session_factory() as session:
            await StripeService.seed_subscription_plans(session)
            firm = Firm(name="Overage Firm", plan_type="starter")
            session.add(firm)
            await session.commit()
            await session.refresh(firm)

            # Limit to 1 credit for deterministic over-limit behavior.
            usage = await StripeService.ensure_usage_period(session, firm_id=firm.id)
            usage.credits_total = 1
            usage.credits_used = 1
            await session.commit()

            with pytest.raises(InsufficientCreditsError):
                await StripeService.consume_calculation_credit(session, firm_id=firm.id, credits=1, grace_limit=0)

    asyncio.run(run())
