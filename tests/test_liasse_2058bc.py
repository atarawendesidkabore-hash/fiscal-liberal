import pytest
from fastapi.testclient import TestClient

from fiscia.app import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_db():
    from fiscia.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_prepare_2058bc_working_draft():
    register_payload = {
        "email": "marie@fiscalia.fr",
        "password": "Fiscalia2026!",
        "full_name": "Marie Fiscaliste",
        "firm_name": "Fiscalia",
        "firm_siren": "123456789",
    }

    register = client.post("/auth/register", json=register_payload)
    assert register.status_code == 201, register.text

    login = client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login.status_code == 200, login.text
    access_token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "liasse": {
            "siren": "987654321",
            "exercice_clos": "2024-12-31",
            "benefice_comptable": 120000,
            "perte_comptable": 0,
            "wi_is_comptabilise": 10000,
            "wg_amendes_penalites": 2000,
            "wm_interets_excedentaires": 3000,
            "wn_reintegrations_diverses": 5000,
            "wv_regime_mere_filiale": 10000,
            "l8_qp_12pct": 0,
        },
        "ca": 5000000,
        "capital_pp": True,
        "annexes": {
            "deficits_reportables_ouverture": 20000,
            "moins_values_lt_ouverture": 8000,
            "moins_values_lt_imputees": 3000,
            "acomptes_verses": 15000,
            "credits_impot": 4000,
            "contribution_sociale": 2500,
            "regularisations": 500,
        },
    }

    response = client.post("/v2/liasse/2058-bc", json=payload, headers=headers)
    assert response.status_code == 200, response.text

    body = response.json()
    table_b = body["tableau_2058b"]
    table_c = body["tableau_2058c"]

    assert table_b["resultat_fiscal_brut"] == 130000.0
    assert table_b["deficits_imputes_exercice"] == 20000.0
    assert table_b["deficits_reportables_cloture"] == 0.0
    assert table_b["moins_values_lt_cloture"] == 5000.0
    assert table_b["base_imposable_apres_reports"] == 110000.0

    assert table_c["tranche_15pct"] == 42500.0
    assert table_c["tranche_25pct"] == 67500.0
    assert table_c["is_total"] == 23250.0
    assert table_c["total_du"] == 26250.0
    assert table_c["total_imputations"] == 19000.0
    assert table_c["solde_a_payer"] == 7250.0
    assert table_c["creance_restante"] == 0.0
    assert body["regime"] == "PME - Taux reduit Art. 219-I-b CGI"
    assert len(body["notes"]) >= 2
