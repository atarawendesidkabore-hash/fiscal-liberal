"""
Tests for GDPR compliance endpoints.
Consent tracking, data export, right-to-deletion, retention policy.
"""
import pytest
from fastapi.testclient import TestClient

from fiscia.app import app


@pytest.fixture(autouse=True)
def _clean_db():
    from fiscia.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def register_and_login(email="gdpr@cabinet.fr", firm=True):
    """Register a user and return auth headers."""
    payload = {
        "email": email,
        "password": "FiscIA2024!Pro",
        "full_name": "GDPR Test User",
    }
    if firm:
        payload["firm_name"] = "Cabinet GDPR"
        payload["firm_siren"] = "999888777"
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/login", json={"email": email, "password": "FiscIA2024!Pro"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# Consent tracking
# ============================================================

def test_grant_consent():
    headers = register_and_login()
    resp = client.post("/gdpr/consent", json={"consent_type": "data_processing", "granted": True}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["consent_type"] == "data_processing"
    assert data["granted"] is True
    assert data["revoked_at"] is None


def test_revoke_consent():
    headers = register_and_login()
    # Grant
    client.post("/gdpr/consent", json={"consent_type": "marketing", "granted": True}, headers=headers)
    # Revoke
    resp = client.post("/gdpr/consent", json={"consent_type": "marketing", "granted": False}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["granted"] is False


def test_list_consents():
    headers = register_and_login()
    client.post("/gdpr/consent", json={"consent_type": "data_processing", "granted": True}, headers=headers)
    client.post("/gdpr/consent", json={"consent_type": "analytics", "granted": True}, headers=headers)
    resp = client.get("/gdpr/consent", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_consent_invalid_type():
    headers = register_and_login()
    resp = client.post("/gdpr/consent", json={"consent_type": "invalid_type", "granted": True}, headers=headers)
    assert resp.status_code == 422


def test_consent_requires_auth():
    resp = client.post("/gdpr/consent", json={"consent_type": "data_processing", "granted": True})
    assert resp.status_code == 401


# ============================================================
# Data export (Art. 20)
# ============================================================

def test_export_data():
    headers = register_and_login()
    # Add a consent
    client.post("/gdpr/consent", json={"consent_type": "data_processing", "granted": True}, headers=headers)
    # Export
    resp = client.get("/gdpr/export", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user" in data
    assert data["user"]["email"] == "gdpr@cabinet.fr"
    assert "consents" in data
    assert len(data["consents"]) >= 1
    assert "calculations" in data
    assert "audit_logs" in data
    assert "exported_at" in data


def test_export_requires_auth():
    resp = client.get("/gdpr/export")
    assert resp.status_code == 401


# ============================================================
# Right to deletion (Art. 17)
# ============================================================

def test_delete_my_data():
    headers = register_and_login(email="delete-me@cabinet.fr")
    # Add consent + a saved calculation
    client.post("/gdpr/consent", json={"consent_type": "data_processing", "granted": True}, headers=headers)
    client.post(
        "/v2/liasse?save=true",
        json={
            "liasse": {
                "siren": "111222333",
                "exercice_clos": "2024-12-31",
                "benefice_comptable": 100000,
                "perte_comptable": 0,
                "wi_is_comptabilise": 5000,
                "wg_amendes_penalites": 1000,
                "wm_interets_excedentaires": 0,
                "wn_reintegrations_diverses": 0,
                "wv_regime_mere_filiale": 0,
            },
            "ca": 5000000,
            "capital_pp": True,
        },
        headers=headers,
    )

    # Delete
    resp = client.delete("/gdpr/delete-me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["deleted"] is True
    assert data["calculations_deleted"] >= 1
    assert data["consents_revoked"] >= 1

    # Verify: user can no longer access protected endpoints (account deactivated)
    # The token is still valid JWT-wise, but user.is_active=False
    resp2 = client.get("/gdpr/export", headers=headers)
    # Depending on implementation, this should fail (403 or 401)
    assert resp2.status_code in (401, 403)


def test_delete_requires_auth():
    resp = client.delete("/gdpr/delete-me")
    assert resp.status_code == 401


# ============================================================
# Retention policy (admin only)
# ============================================================

def test_retention_report():
    headers = register_and_login()  # admin (has firm)
    resp = client.get("/gdpr/retention/report", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_calculations" in data
    assert "expired_calculations" in data
    assert data["retention_days"] == 365 * 3


def test_retention_purge():
    headers = register_and_login()  # admin
    resp = client.post("/gdpr/retention/purge", headers=headers)
    assert resp.status_code == 200
    assert "purged" in resp.json()


def test_retention_report_requires_admin():
    """Non-admin users cannot access retention endpoints."""
    # Register admin first to create firm
    register_and_login(email="admin@firm.fr")

    # Register client user (no firm = client role)
    client.post("/auth/register", json={
        "email": "client@firm.fr",
        "password": "FiscIA2024!Pro",
        "full_name": "Client User",
    })
    resp = client.post("/auth/login", json={"email": "client@firm.fr", "password": "FiscIA2024!Pro"})
    client_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    resp = client.get("/gdpr/retention/report", headers=client_headers)
    assert resp.status_code == 403
