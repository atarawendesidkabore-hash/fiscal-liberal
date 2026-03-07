"""Client dossier route placeholders."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("")
async def list_clients() -> dict:
    return {"items": []}

