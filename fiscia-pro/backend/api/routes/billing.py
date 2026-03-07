"""Stripe billing routes scaffold."""

from __future__ import annotations

from fastapi import APIRouter

from ...config import PLANS

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans")
async def get_plans() -> dict:
    return {"plans": PLANS}


@router.post("/webhook")
async def stripe_webhook() -> dict:
    return {"received": True}

