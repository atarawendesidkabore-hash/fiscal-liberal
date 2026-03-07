"""Standalone IS calculation route."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel

from ...services import ISCalculator

router = APIRouter(prefix="/is-calcul", tags=["is_calcul"])


class CalculISInput(BaseModel):
    rf: Decimal
    ca_ht: Decimal
    capital_75pct_pp: bool


@router.post("")
async def calculer_is(payload: CalculISInput) -> dict:
    calc = ISCalculator()
    result = calc.calculer_is(payload.rf, payload.ca_ht, payload.capital_75pct_pp)
    return result.dict()

