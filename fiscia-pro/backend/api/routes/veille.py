"""Fiscal alerts route placeholder."""

from __future__ import annotations

from fastapi import APIRouter

from ...services.veille_fiscale import VeilleFiscaleService

router = APIRouter(prefix="/veille", tags=["veille"])


@router.get("/sources")
async def list_sources() -> dict:
    service = VeilleFiscaleService()
    return {"sources": service.list_sources()}

