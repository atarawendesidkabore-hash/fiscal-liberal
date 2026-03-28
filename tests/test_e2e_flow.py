"""
End-to-end smoke test: full auth + calculation + audit flow.
Register firm → Login → Calculate IS via /v2/liasse → Verify saved → Check audit log.
"""
import pytest
from fastapi.testclient import TestClient

from fiscia.app import app


@pytest.fixture(autouse=True)
def _clean_db():
    """Ensure fresh tables for each test run."""
    from fiscia.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

REGISTER_PAYLOAD = {
    "email": "jean@cabinet-dupont.fr",
    "password": "FiscIA2024!Pro",
    "full_name": "Jean Dupont",
    "firm_name": "Cabinet Dupont & Associes",
    "firm_siren": "123456789",
}

LIASSE_PAYLOAD = {
    "liasse": {
        "siren": "987654321",
        "exercice_clos": "2024-12-31",
        "benefice_comptable": 120000,
        "perte_comptable": 0,
        "wi_is_comptabilise": 10000,
        "wg_amendes_penalites": 2000,
        "wm_interets_excedentaires": 3000,
        "wn_reintegrations_diverses": 0,
        "wv_regime_mere_filiale": 0,
        "l8_qp_12pct": 0,
    },
    "ca": 5000000,
    "capital_pp": True,
}


def test_e2e_full_flow():
    """Complete auth + calculation + audit pipeline."""

    # ── Step 1: Health check ──
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("STEP 1 OK: Health check passed")

    # ── Step 2: Register firm + admin user ──
    r = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert r.status_code == 201, f"Register failed: {r.text}"
    user_data = r.json()
    assert user_data["role"] == "admin"
    assert user_data["firm_id"] is not None
    user_id = user_data["id"]
    firm_id = user_data["firm_id"]
    print(f"STEP 2 OK: Registered user={user_id}, firm={firm_id}, role=admin")

    # ── Step 3: Duplicate registration blocked ──
    r = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert r.status_code == 409
    print("STEP 3 OK: Duplicate email rejected (409)")

    # ── Step 4: Login ──
    r = client.post("/auth/login", json={
        "email": "jean@cabinet-dupont.fr",
        "password": "FiscIA2024!Pro",
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    tokens = r.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] == 900  # 15 min
    print("STEP 4 OK: Login successful, got access + refresh tokens")

    # ── Step 5: Wrong password rejected ──
    r = client.post("/auth/login", json={
        "email": "jean@cabinet-dupont.fr",
        "password": "WrongPassword",
    })
    assert r.status_code == 401
    print("STEP 5 OK: Wrong password rejected (401)")

    # ── Step 6: GET /auth/me ──
    headers = {"Authorization": f"Bearer {access_token}"}
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == "jean@cabinet-dupont.fr"
    assert me["role"] == "admin"
    print(f"STEP 6 OK: /auth/me returned role={me['role']}")

    # ── Step 7: Unauthenticated v2 request blocked ──
    r = client.post("/v2/liasse", json=LIASSE_PAYLOAD)
    assert r.status_code in (401, 403)
    print("STEP 7 OK: Unauthenticated /v2/liasse blocked")

    # ── Step 8: Calculate + save via /v2/liasse (authenticated) ──
    r = client.post(
        "/v2/liasse?save=true",
        json=LIASSE_PAYLOAD,
        headers=headers,
    )
    assert r.status_code == 200, f"Liasse calc failed: {r.text}"
    result = r.json()
    # 120k benefice + 10k IS + 2k amendes + 3k interets = 135k RF brut
    # IS PME: 42,500 * 15% + 92,500 * 25% = 6,375 + 23,125 = 29,500
    assert result["rf_brut"] == 135000.0
    assert result["is_total"] == 29500.0
    assert result["regime"] == "PME - Taux reduit Art. 219-I-b CGI"
    assert "saved_id" in result
    saved_id = result["saved_id"]
    print(f"STEP 8 OK: IS calculated — RF={result['rf_brut']}, IS={result['is_total']}, saved_id={saved_id}")

    # ── Step 9: Retrieve saved calculation ──
    r = client.get(f"/v2/liasse/saved/{saved_id}", headers=headers)
    assert r.status_code == 200
    saved = r.json()
    assert saved["siren"] == "987654321"
    assert saved["result_data"]["is_total"] == 29500.0
    print(f"STEP 9 OK: Retrieved saved calculation — siren={saved['siren']}")

    # ── Step 10: List saved calculations ──
    r = client.get("/v2/liasse/saved", headers=headers)
    assert r.status_code == 200
    listing = r.json()
    assert listing["count"] == 1
    print(f"STEP 10 OK: Listed {listing['count']} saved calculation(s)")

    # ── Step 11: Audit log (admin only) ──
    r = client.get("/audit-logs", headers=headers)
    assert r.status_code == 200
    logs = r.json()
    assert logs["count"] >= 1
    actions = [log["action"] for log in logs["results"]]
    assert "create_liasse" in actions
    print(f"STEP 11 OK: Audit log has {logs['count']} entries, actions={actions}")

    # ── Step 12: Delete calculation (admin has fiscaliste+ access) ──
    r = client.delete(f"/v2/liasse/saved/{saved_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["deleted"] is True
    print(f"STEP 12 OK: Deleted saved calculation {saved_id}")

    # ── Step 13: Verify deletion ──
    r = client.get(f"/v2/liasse/saved/{saved_id}", headers=headers)
    assert r.status_code == 404
    print("STEP 13 OK: Deleted calculation returns 404")

    # ── Step 14: Token refresh ──
    r = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    new_tokens = r.json()
    assert new_tokens["access_token"] != access_token
    print("STEP 14 OK: Token refresh returned new access token")

    # ── Step 15: Old refresh token blocked (rotation) ──
    r = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 401
    print("STEP 15 OK: Old refresh token rejected after rotation")

    # ── Step 16: Prometheus metrics available ──
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.text
    assert "fiscia_http_requests_total" in body
    assert "fiscia_liasse_calculations_total" in body
    print("STEP 16 OK: /metrics exposes Prometheus counters")

    # ── Step 17: Sync v1 endpoints still work (no auth) ──
    r = client.post("/calc-is", json={"ca": 5000000, "capital_pp": True})
    assert r.status_code == 200
    assert r.json()["regime"] == "PME - Taux reduit Art. 219-I-b CGI"
    print("STEP 17 OK: v1 /calc-is works without auth (backward compat)")

    print("\n" + "=" * 60)
    print("ALL 17 STEPS PASSED — End-to-end flow verified.")
    print("=" * 60)
