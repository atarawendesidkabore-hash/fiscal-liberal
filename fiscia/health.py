"""
Enhanced health checks for FiscIA Pro.
Aggregates database, Ollama, and application status.
"""
import logging
import os
import time

import httpx

from fiscia.database import check_database_health
from fiscia.database_async import check_async_database_health

logger = logging.getLogger("fiscia.health")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "fiscia-fiscal-is-v3")


async def check_ollama_health() -> dict:
    """Check if Ollama is running and the fiscal model is loaded."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_HOST}/api/version")
            if resp.status_code != 200:
                return {"status": "error", "detail": f"HTTP {resp.status_code}"}
            version_info = resp.json()

            # Check if target model is available
            tags_resp = await client.get(f"{OLLAMA_HOST}/api/tags")
            models = []
            model_loaded = False
            if tags_resp.status_code == 200:
                models = [m.get("name", "") for m in tags_resp.json().get("models", [])]
                model_loaded = any(OLLAMA_MODEL in m for m in models)

            return {
                "status": "ok" if model_loaded else "degraded",
                "ollama_version": version_info.get("version", "unknown"),
                "target_model": OLLAMA_MODEL,
                "model_loaded": model_loaded,
                "available_models": len(models),
            }
    except httpx.ConnectError:
        return {"status": "unavailable", "detail": "Ollama not reachable"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def check_sync_db_health() -> dict:
    """Sync database health with timing."""
    start = time.perf_counter()
    result = check_database_health()
    result["response_time_ms"] = round((time.perf_counter() - start) * 1000, 2)
    return result


async def check_full_health(include_ollama: bool = True) -> dict:
    """Aggregate health check across all subsystems."""
    checks = {}

    # Async DB check
    start = time.perf_counter()
    db_result = await check_async_database_health()
    db_result["response_time_ms"] = round((time.perf_counter() - start) * 1000, 2)
    checks["database"] = db_result

    # Ollama check (optional — skip in test/CI)
    if include_ollama:
        checks["ollama"] = await check_ollama_health()

    # Overall status: ok if all critical services ok, degraded if non-critical down
    db_ok = checks["database"]["status"] == "ok"
    ollama_ok = checks.get("ollama", {}).get("status") in ("ok", "degraded", None)

    if db_ok and ollama_ok:
        overall = "ok"
    elif db_ok:
        overall = "degraded"
    else:
        overall = "unhealthy"

    return {
        "status": overall,
        "version": "3.0",
        "checks": checks,
    }
