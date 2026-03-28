"""
FiscIA Pro — Ollama integration client.
Async httpx client for local Ollama inference (fiscal AI reasoning).
"""
import logging
import os
import time
from typing import Optional

import httpx

logger = logging.getLogger("fiscia.ollama")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "fiscia-fiscal-is-v3")
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "120"))

# --- System prompts for each reasoning mode ---

SYSTEM_PROMPT_IS = (
    "Tu es FiscIA Local IS, le moteur fiscal embarque de FiscIA Pro. "
    "Contexte: Art. 219 CGI, LFI 2024. Taux normal 25%. "
    "Taux reduit PME 15% sur premiers 42 500 EUR si CA HT < 10M EUR "
    "et capital >= 75% PP. Reponds de facon structuree avec les montants exacts."
)

SYSTEM_PROMPT_LIASSE = (
    "Tu es FiscIA Liasse, l'assistant de determination du resultat fiscal IS. "
    "Reference: formulaire DGFiP 2058-A, LFI 2024. "
    "Pour chaque charge, indique le code ligne 2058-A exact, le sens "
    "(REINTEGRATION ou DEDUCTION), l'article CGI applicable, le montant, "
    "et l'impact sur le RF."
)

SYSTEM_PROMPT_MERE = (
    "Tu es FiscIA Art145, le verificateur du regime mere-filiale. "
    "Reference: Art. 145 et 216 CGI, LFI 2024. "
    "Verifie les 6 conditions cumulatives Art. 145 CGI une par une. "
    "Si eligible, calcule la deduction WV, la reintegration WN (QP 5%), "
    "et l'impact RF net."
)

SYSTEM_PROMPT_GENERAL = (
    "Tu es FiscIA Pro, un assistant fiscal specialise en IS francais (Art. 219 CGI, LFI 2024). "
    "Tu reponds uniquement aux questions de fiscalite des entreprises. "
    "Cite toujours les articles CGI applicables. "
    "Ajoute toujours: 'Reponse indicative. Validation professionnelle requise.'"
)

SYSTEM_PROMPTS = {
    "is": SYSTEM_PROMPT_IS,
    "liasse": SYSTEM_PROMPT_LIASSE,
    "mere": SYSTEM_PROMPT_MERE,
    "general": SYSTEM_PROMPT_GENERAL,
}


class OllamaError(Exception):
    """Raised when Ollama API returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int = 503):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def generate(
    prompt: str,
    mode: str = "general",
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.05,
    max_tokens: int = 4096,
) -> dict:
    """
    Send a prompt to Ollama and return the generated response.

    Args:
        prompt: The user prompt.
        mode: One of "is", "liasse", "mere", "general". Selects the system prompt.
        system: Override the system prompt entirely.
        model: Override the model name.
        temperature: Sampling temperature (default 0.05 for deterministic fiscal output).
        max_tokens: Max tokens in the response.

    Returns:
        dict with keys: response, model, mode, elapsed_ms, tokens_evaluated, tokens_generated
    """
    system_prompt = system or SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPT_GENERAL)
    target_model = model or OLLAMA_MODEL

    payload = {
        "model": target_model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            resp = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
    except httpx.ConnectError:
        raise OllamaError("Ollama non accessible. Verifiez que le serveur est demarre.")
    except httpx.TimeoutException:
        raise OllamaError("Ollama timeout. Le modele met trop de temps a repondre.", 504)
    except httpx.HTTPError as e:
        raise OllamaError(f"Erreur HTTP Ollama: {e}")

    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

    if resp.status_code != 200:
        detail = resp.text[:500]
        raise OllamaError(f"Ollama HTTP {resp.status_code}: {detail}", resp.status_code)

    data = resp.json()
    response_text = data.get("response", "")

    logger.info(
        "ollama_generate",
        extra={
            "model": target_model,
            "mode": mode,
            "prompt_len": len(prompt),
            "response_len": len(response_text),
            "elapsed_ms": elapsed_ms,
        },
    )

    return {
        "response": response_text,
        "model": data.get("model", target_model),
        "mode": mode,
        "elapsed_ms": elapsed_ms,
        "tokens_evaluated": data.get("prompt_eval_count", 0),
        "tokens_generated": data.get("eval_count", 0),
        "disclaimer": "Reponse indicative generee par IA locale. Validation professionnelle requise.",
    }


async def check_available() -> bool:
    """Quick check: is Ollama reachable?"""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_HOST}/api/version")
            return resp.status_code == 200
    except Exception:
        return False
