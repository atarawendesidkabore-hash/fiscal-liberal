"""Tests d'authentification."""


class TestAuth:
    def test_register(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "new@fiscal.fr",
            "password": "pass123",
            "full_name": "Marie Test",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@fiscal.fr"
        assert data["full_name"] == "Marie Test"
        assert "id" in data

    def test_register_duplicate(self, client):
        client.post("/api/auth/register", json={
            "email": "dup@fiscal.fr",
            "password": "pass123",
            "full_name": "Dup Test",
        })
        resp = client.post("/api/auth/register", json={
            "email": "dup@fiscal.fr",
            "password": "pass456",
            "full_name": "Dup Test 2",
        })
        assert resp.status_code == 400

    def test_login(self, client):
        client.post("/api/auth/register", json={
            "email": "login@fiscal.fr",
            "password": "pass123",
            "full_name": "Login Test",
        })
        resp = client.post("/api/auth/login", data={
            "username": "login@fiscal.fr",
            "password": "pass123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "email": "wrong@fiscal.fr",
            "password": "pass123",
            "full_name": "Wrong Test",
        })
        resp = client.post("/api/auth/login", data={
            "username": "wrong@fiscal.fr",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_me(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@fiscal.fr"

    def test_me_no_token(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
