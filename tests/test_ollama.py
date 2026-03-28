"""
Tests for Ollama integration — client + API routes.
All tests mock httpx to avoid requiring a running Ollama instance.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from fiscia.app import app
from fiscia.ollama_client import generate, check_available, OllamaError, SYSTEM_PROMPTS


@pytest.fixture(autouse=True)
def _clean_db():
    """Ensure fresh tables for each test run."""
    from fiscia.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# --- Helper: register + login, return auth header ---

def auth_header() -> dict:
    client.post("/auth/register", json={
        "email": "test@cabinet.fr",
        "password": "FiscIA2024!Pro",
        "full_name": "Test User",
        "firm_name": "Cabinet Test",
        "firm_siren": "111222333",
    })
    resp = client.post("/auth/login", json={"email": "test@cabinet.fr", "password": "FiscIA2024!Pro"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Mock Ollama response factory ---

def mock_ollama_response(text="Resultat fiscal: 100 000 EUR. IS total: 25 000 EUR."):
    """Create a mock httpx.Response mimicking Ollama /api/generate."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "model": "fiscia-fiscal-is-v3",
        "response": text,
        "done": True,
        "prompt_eval_count": 150,
        "eval_count": 80,
    }
    return resp


def mock_version_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"version": "0.5.0"}
    return resp


# ============================================================
# Unit tests: ollama_client.py
# ============================================================

@pytest.mark.asyncio
async def test_generate_success():
    """generate() returns structured response on success."""
    mock_resp = mock_ollama_response("IS PME: 42 500 x 15% = 6 375 EUR")
    with patch("fiscia.ollama_client.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.post.return_value = mock_resp
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await generate("Calcule IS pour RF=100k", mode="is")

    assert result["response"] == "IS PME: 42 500 x 15% = 6 375 EUR"
    assert result["mode"] == "is"
    assert result["model"] == "fiscia-fiscal-is-v3"
    assert result["tokens_evaluated"] == 150
    assert result["tokens_generated"] == 80
    assert "disclaimer" in result
    assert result["elapsed_ms"] >= 0


@pytest.mark.asyncio
async def test_generate_connect_error():
    """generate() raises OllamaError on connection failure."""
    import httpx as _httpx
    with patch("fiscia.ollama_client.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.post.side_effect = _httpx.ConnectError("Connection refused")
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(OllamaError, match="non accessible"):
            await generate("test prompt")


@pytest.mark.asyncio
async def test_generate_timeout():
    """generate() raises OllamaError on timeout."""
    import httpx as _httpx
    with patch("fiscia.ollama_client.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.post.side_effect = _httpx.TimeoutException("timed out")
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(OllamaError, match="timeout") as exc_info:
            await generate("test prompt")
        assert exc_info.value.status_code == 504


@pytest.mark.asyncio
async def test_generate_http_error():
    """generate() raises OllamaError on non-200 response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"
    with patch("fiscia.ollama_client.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.post.return_value = mock_resp
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(OllamaError, match="HTTP 500"):
            await generate("test prompt")


@pytest.mark.asyncio
async def test_generate_custom_mode():
    """generate() uses correct system prompt for each mode."""
    for mode in ("is", "liasse", "mere", "general"):
        mock_resp = mock_ollama_response(f"Response for {mode}")
        with patch("fiscia.ollama_client.httpx.AsyncClient") as MockClient:
            instance = AsyncMock()
            instance.post.return_value = mock_resp
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = instance

            result = await generate("test", mode=mode)
            assert result["mode"] == mode

            # Verify the system prompt was sent
            call_args = instance.post.call_args
            payload = call_args[1]["json"]
            assert payload["system"] == SYSTEM_PROMPTS[mode]


@pytest.mark.asyncio
async def test_check_available_true():
    """check_available() returns True when Ollama responds."""
    with patch("fiscia.ollama_client.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get.return_value = mock_version_response()
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        assert await check_available() is True


@pytest.mark.asyncio
async def test_check_available_false():
    """check_available() returns False when Ollama is down."""
    import httpx as _httpx
    with patch("fiscia.ollama_client.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get.side_effect = _httpx.ConnectError("refused")
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        assert await check_available() is False


# ============================================================
# API route tests: /v2/ai/*
# ============================================================

def test_ai_status():
    """GET /v2/ai/status returns availability info (no auth required)."""
    with patch("fiscia.app.ollama_available", new_callable=AsyncMock, return_value=True):
        resp = client.get("/v2/ai/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] is True
    assert "model" in data


def test_ai_explain_requires_auth():
    """POST /v2/ai/explain rejects unauthenticated requests."""
    resp = client.post("/v2/ai/explain", json={"prompt": "Calcule IS pour 100k"})
    assert resp.status_code == 401


def test_ai_explain_success():
    """POST /v2/ai/explain returns Ollama response with auth."""
    headers = auth_header()
    mock_result = {
        "response": "IS = 25 000 EUR (taux normal 25%)",
        "model": "fiscia-fiscal-is-v3",
        "mode": "general",
        "elapsed_ms": 1500,
        "tokens_evaluated": 100,
        "tokens_generated": 50,
        "disclaimer": "Reponse indicative.",
    }
    with patch("fiscia.app.ollama_generate", new_callable=AsyncMock, return_value=mock_result):
        resp = client.post(
            "/v2/ai/explain",
            json={"prompt": "Calcule IS pour resultat fiscal 100 000 EUR", "mode": "is"},
            headers=headers,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "IS = 25 000 EUR" in data["response"]
    assert data["mode"] == "general"


def test_ai_explain_ollama_down():
    """POST /v2/ai/explain returns 503 when Ollama is unreachable."""
    headers = auth_header()
    with patch("fiscia.app.ollama_generate", new_callable=AsyncMock, side_effect=OllamaError("Ollama non accessible")):
        resp = client.post(
            "/v2/ai/explain",
            json={"prompt": "Calcule IS pour 100k euros de RF"},
            headers=headers,
        )
    assert resp.status_code == 503


def test_ai_explain_validation():
    """POST /v2/ai/explain rejects too-short prompts."""
    headers = auth_header()
    resp = client.post(
        "/v2/ai/explain",
        json={"prompt": "IS?", "mode": "is"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_ai_explain_is():
    """POST /v2/ai/explain-is sends IS calculation to Ollama."""
    headers = auth_header()
    mock_result = {
        "response": "Tranche 15%: 42 500 x 15% = 6 375. Tranche 25%: 57 500 x 25% = 14 375. IS total = 20 750.",
        "model": "fiscia-fiscal-is-v3",
        "mode": "is",
        "elapsed_ms": 2000,
        "tokens_evaluated": 120,
        "tokens_generated": 90,
        "disclaimer": "Reponse indicative.",
    }
    with patch("fiscia.app.ollama_generate", new_callable=AsyncMock, return_value=mock_result):
        resp = client.post(
            "/v2/ai/explain-is",
            json={"ca": 5000000, "capital_pp": True},
            headers=headers,
        )
    assert resp.status_code == 200
    assert "20 750" in resp.json()["response"]


def test_ai_explain_liasse():
    """POST /v2/ai/explain-liasse sends liasse data to Ollama."""
    headers = auth_header()
    mock_result = {
        "response": "WI: +10 000 (Art. 213). WG: +2 000 (Art. 39-2). RF brut = 135 000.",
        "model": "fiscia-fiscal-is-v3",
        "mode": "liasse",
        "elapsed_ms": 3000,
        "tokens_evaluated": 200,
        "tokens_generated": 150,
        "disclaimer": "Reponse indicative.",
    }
    with patch("fiscia.app.ollama_generate", new_callable=AsyncMock, return_value=mock_result):
        resp = client.post(
            "/v2/ai/explain-liasse",
            json={
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
                },
                "ca": 5000000,
                "capital_pp": True,
            },
            headers=headers,
        )
    assert resp.status_code == 200
    assert "RF brut = 135 000" in resp.json()["response"]


def test_ai_explain_mere():
    """POST /v2/ai/explain-mere sends Art. 145 data to Ollama."""
    headers = auth_header()
    mock_result = {
        "response": "6 conditions verifiees: ELIGIBLE. Deduction WV = 50 000. QP 5% WN = 2 500. Impact RF = -47 500.",
        "model": "fiscia-fiscal-is-v3",
        "mode": "mere",
        "elapsed_ms": 2500,
        "tokens_evaluated": 180,
        "tokens_generated": 100,
        "disclaimer": "Reponse indicative.",
    }
    with patch("fiscia.app.ollama_generate", new_callable=AsyncMock, return_value=mock_result):
        resp = client.post(
            "/v2/ai/explain-mere",
            json={
                "pct_capital": 7.0,
                "annees_detention": 3,
                "nominatif": True,
                "pleine_propriete": True,
                "filiale_is": True,
                "paradis_fiscal": False,
                "dividende_brut": 50000,
                "credit_impot": 0,
            },
            headers=headers,
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "ELIGIBLE" in data["response"]
    assert "47 500" in data["response"]
