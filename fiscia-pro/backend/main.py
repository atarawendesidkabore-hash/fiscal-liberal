"""FastAPI entry point for FiscIA Pro backend."""

from __future__ import annotations

from fastapi import FastAPI

from .api.routes import assistant, auth, billing, clients, is_calcul, liasse_2058a, recherche_cgi, veille

app = FastAPI(
    title="FiscIA Pro API",
    version="0.1.0",
    description="SaaS fiscal IA - backend scaffold aligned with Master Build Prompt v3",
)

app.include_router(auth.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(liasse_2058a.router, prefix="/api")
app.include_router(is_calcul.router, prefix="/api")
app.include_router(recherche_cgi.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(veille.router, prefix="/api")
app.include_router(billing.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "service": "fiscia-pro-backend"}

