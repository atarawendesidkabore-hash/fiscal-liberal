from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from fiscia.app import app
from fiscia.auth_endpoints import reset_auth_rate_limiter_for_tests
from fiscia.auth_models import JWT_ALGORITHM, User, get_jwt_secret, hash_password
from fiscia.dependencies import get_async_db_session
from fiscia.models_db import Base


@pytest.fixture()
def client() -> TestClient:
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
        test_client.app.state.test_session_factory = session_factory
        yield test_client

    app.dependency_overrides.clear()
    reset_auth_rate_limiter_for_tests()
    asyncio.run(engine.dispose())


def _register(client: TestClient, *, firm_name: str, email: str, password: str) -> dict:
    response = client.post(
        "/auth/register",
        json={
            "firm_name": firm_name,
            "plan_type": "pro",
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _login(client: TestClient, *, email: str, password: str) -> dict:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_auth_register_login_and_me_flow(client: TestClient) -> None:
    register_data = _register(
        client,
        firm_name="Cabinet Horizon",
        email="admin@horizon.fr",
        password="SecurePass!123",
    )
    assert register_data["user"]["role"] == "admin"
    assert register_data["tokens"]["access_token"]
    assert register_data["tokens"]["refresh_token"]

    login_data = _login(client, email="admin@horizon.fr", password="SecurePass!123")
    access_token = login_data["tokens"]["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_response.status_code == 200
    me_json = me_response.json()
    assert me_json["email"] == "admin@horizon.fr"
    assert me_json["role"] == "admin"


def test_auth_refresh_rotation_and_logout_blacklist(client: TestClient) -> None:
    _register(
        client,
        firm_name="Cabinet Atlas",
        email="admin@atlas.fr",
        password="StrongPass!456",
    )
    login_data = _login(client, email="admin@atlas.fr", password="StrongPass!456")

    access_token = login_data["tokens"]["access_token"]
    old_refresh = login_data["tokens"]["refresh_token"]

    refresh_response = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_response.status_code == 200
    new_refresh = refresh_response.json()["refresh_token"]
    assert new_refresh != old_refresh

    reused_response = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert reused_response.status_code == 401

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": new_refresh},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_response.status_code == 200

    revoked_response = client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert revoked_response.status_code == 401


def test_rbac_blocks_client_role_on_fiscal_endpoint(client: TestClient) -> None:
    admin_data = _register(
        client,
        firm_name="Cabinet Delta",
        email="admin@delta.fr",
        password="DeltaPass!789",
    )

    firm_id = admin_data["user"]["firm_id"]
    session_factory = client.app.state.test_session_factory

    async def _create_client_user() -> None:
        async with session_factory() as session:
            async with session.begin():
                session.add(
                    User(
                        email="client@delta.fr",
                        hashed_password=hash_password("ClientPass!789"),
                        role="client",
                        firm_id=firm_id,
                        is_active=True,
                    )
                )

    asyncio.run(_create_client_user())

    client_login = _login(client, email="client@delta.fr", password="ClientPass!789")
    client_access = client_login["tokens"]["access_token"]

    blocked_response = client.post(
        "/calc-is",
        json={"ca": 5000000, "capital_pp": True, "rf": 100000},
        headers={"Authorization": f"Bearer {client_access}"},
    )
    assert blocked_response.status_code == 403

    admin_access = admin_data["tokens"]["access_token"]
    allowed_response = client.post(
        "/calc-is",
        json={"ca": 5000000, "capital_pp": True, "rf": 100000},
        headers={"Authorization": f"Bearer {admin_access}"},
    )
    assert allowed_response.status_code == 200


def test_firm_data_isolation_and_expired_access_token(client: TestClient) -> None:
    firm_a = _register(
        client,
        firm_name="Cabinet Alpha",
        email="admin@alpha.fr",
        password="AlphaPass!123",
    )
    firm_b = _register(
        client,
        firm_name="Cabinet Beta",
        email="admin@beta.fr",
        password="BetaPass!123",
    )

    admin_a_access = firm_a["tokens"]["access_token"]
    admin_b_id = firm_b["user"]["id"]

    forbidden_response = client.post(
        "/liasse",
        json={
            "user_id": admin_b_id,
            "ca": 6500000,
            "capital_pp": True,
            "liasse": {
                "siren": "123456789",
                "exercice_clos": "2024-12-31",
                "benefice_comptable": "120000",
                "perte_comptable": "0",
                "wi_is_comptabilise": "10000",
                "wg_amendes_penalites": "2000",
                "wm_interets_excedentaires": "8000",
                "wn_reintegrations_diverses": "0",
                "wv_regime_mere_filiale": "30000",
                "l8_qp_12pct": "5000",
            },
        },
        headers={"Authorization": f"Bearer {admin_a_access}"},
    )
    assert forbidden_response.status_code == 403

    expired_access = jwt.encode(
        {
            "sub": str(firm_a["user"]["id"]),
            "email": firm_a["user"]["email"],
            "role": "admin",
            "firm_id": firm_a["user"]["firm_id"],
            "type": "access",
            "jti": "expired-jti",
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
            "exp": int((datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp()),
        },
        get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )

    expired_response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired_access}"})
    assert expired_response.status_code == 401