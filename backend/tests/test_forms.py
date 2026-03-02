"""Tests des formulaires 2058-A/B/C via l'API."""

import pytest


@pytest.fixture
def exercice_id(client, auth_headers):
    """Crée une société + exercice, retourne l'exercice_id."""
    resp = client.post("/api/companies", json={
        "raison_sociale": "SELARL Test Avocat",
        "forme_juridique": "SELARL",
        "siren": "123456789",
        "capital_social": 10000.0,
    }, headers=auth_headers)
    company_id = resp.json()["id"]

    resp = client.post("/api/exercices", json={
        "company_id": company_id,
        "date_debut": "2025-01-01",
        "date_fin": "2025-12-31",
    }, headers=auth_headers)
    return resp.json()["id"]


class TestForm2058A:
    def test_get_empty_form(self, client, auth_headers, exercice_id):
        resp = client.get(f"/api/exercices/{exercice_id}/2058a", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["wa_resultat_comptable"] == 0.0
        assert data["wu_resultat_fiscal"] == 0.0

    def test_save_and_auto_calculate(self, client, auth_headers, exercice_id):
        resp = client.put(f"/api/exercices/{exercice_id}/2058a", json={
            "wa_resultat_comptable": 100000.0,
            "wh_amendes_penalites": 5000.0,
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ws_total_reintegrations"] == 5000.0
        assert data["wt_total_deductions"] == 0.0
        assert data["wu_resultat_fiscal"] == 105000.0

    def test_calculate_endpoint(self, client, auth_headers, exercice_id):
        client.put(f"/api/exercices/{exercice_id}/2058a", json={
            "wa_resultat_comptable": 200000.0,
            "wh_amendes_penalites": 3000.0,
            "wn_produits_participation": 10000.0,
        }, headers=auth_headers)
        resp = client.post(f"/api/exercices/{exercice_id}/2058a/calculate", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["ws_total_reintegrations"] == 3000.0
        assert data["wt_total_deductions"] == 10000.0
        assert data["wu_resultat_fiscal"] == 193000.0
        assert data["is_benefice"] is True

    def test_validate_clean(self, client, auth_headers, exercice_id):
        client.put(f"/api/exercices/{exercice_id}/2058a", json={
            "wa_resultat_comptable": 50000.0,
        }, headers=auth_headers)
        resp = client.post(f"/api/exercices/{exercice_id}/2058a/validate", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["valide"] is True

    def test_validate_with_info(self, client, auth_headers, exercice_id):
        client.put(f"/api/exercices/{exercice_id}/2058a", json={
            "wa_resultat_comptable": 50000.0,
            "wh_amendes_penalites": 1000.0,
            "we_amortissements_excessifs": 3000.0,
        }, headers=auth_headers)
        resp = client.post(f"/api/exercices/{exercice_id}/2058a/validate", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        # Info messages (not errors) → still valid
        assert data["valide"] is True
        assert len(data["messages"]) >= 2  # WE info + WH info


class TestForm2058B:
    def test_get_empty(self, client, auth_headers, exercice_id):
        resp = client.get(f"/api/exercices/{exercice_id}/2058b", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0.0

    def test_add_item(self, client, auth_headers, exercice_id):
        resp = client.post(f"/api/exercices/{exercice_id}/2058b/items", json={
            "nature": "Amende stationnement",
            "montant": 135.0,
            "article_cgi": "Art. 39-2",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nature"] == "Amende stationnement"
        assert data["montant"] == 135.0

    def test_add_multiple_and_total(self, client, auth_headers, exercice_id):
        client.post(f"/api/exercices/{exercice_id}/2058b/items", json={
            "nature": "Amende fiscale",
            "montant": 500.0,
        }, headers=auth_headers)
        client.post(f"/api/exercices/{exercice_id}/2058b/items", json={
            "nature": "Pénalité retard TVA",
            "montant": 200.0,
        }, headers=auth_headers)
        resp = client.get(f"/api/exercices/{exercice_id}/2058b", headers=auth_headers)
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 700.0

    def test_delete_item(self, client, auth_headers, exercice_id):
        resp = client.post(f"/api/exercices/{exercice_id}/2058b/items", json={
            "nature": "Test delete",
            "montant": 100.0,
        }, headers=auth_headers)
        item_id = resp.json()["id"]
        resp = client.delete(
            f"/api/exercices/{exercice_id}/2058b/items/{item_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204


class TestForm2058C:
    def test_get_empty(self, client, auth_headers, exercice_id):
        resp = client.get(f"/api/exercices/{exercice_id}/2058c", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["resultat_exercice"] == 0.0

    def test_save(self, client, auth_headers, exercice_id):
        resp = client.put(f"/api/exercices/{exercice_id}/2058c", json={
            "resultat_exercice": 80000.0,
            "dividendes_distribues": 30000.0,
            "reserves_legales": 4000.0,
            "report_a_nouveau_nouveau": 46000.0,
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["resultat_exercice"] == 80000.0
        assert data["dividendes_distribues"] == 30000.0


class TestDashboard:
    def test_dashboard(self, client, auth_headers):
        # Create company
        resp = client.post("/api/companies", json={
            "raison_sociale": "SELAS Dashboard Test",
            "forme_juridique": "SELAS",
        }, headers=auth_headers)
        company_id = resp.json()["id"]

        # Create exercice
        resp = client.post("/api/exercices", json={
            "company_id": company_id,
            "date_debut": "2024-01-01",
            "date_fin": "2024-12-31",
        }, headers=auth_headers)
        ex_id = resp.json()["id"]

        # Fill 2058-A
        client.put(f"/api/exercices/{ex_id}/2058a", json={
            "wa_resultat_comptable": 120000.0,
            "wh_amendes_penalites": 2000.0,
        }, headers=auth_headers)

        # Check dashboard
        resp = client.get(f"/api/dashboard/{company_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["nb_exercices"] == 1
        assert data["dernier_exercice"]["resultat_fiscal"] == 122000.0


class TestExportPDF:
    def test_export_2058a(self, client, auth_headers, exercice_id):
        # Fill form first
        client.put(f"/api/exercices/{exercice_id}/2058a", json={
            "wa_resultat_comptable": 50000.0,
            "wh_amendes_penalites": 1000.0,
        }, headers=auth_headers)
        resp = client.post(
            f"/api/exercices/{exercice_id}/export/pdf?formulaire=2058a",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert len(resp.content) > 100  # PDF has content

    def test_export_invalid_form(self, client, auth_headers, exercice_id):
        resp = client.post(
            f"/api/exercices/{exercice_id}/export/pdf?formulaire=invalid",
            headers=auth_headers,
        )
        assert resp.status_code == 400
