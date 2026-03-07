from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.auth_endpoints import router as auth_router
from fiscia.auth_models import Role, User
from fiscia.billing_endpoints import router as billing_router
from fiscia.cgi_search import search as cgi_search
from fiscia.crud import CrudError, create_audit_log, create_calculation
from fiscia.database import database_health_check
from fiscia.dependencies import get_async_db_session
from fiscia.guardrails import GuardrailError, MANDATORY_DISCLAIMER, enforce_guardrails
from fiscia.is_calculator import ISCalculator
from fiscia.mere_fi_check import verifier_mere_filiale
from fiscia.models import Liasse2058AInput
from fiscia.rbac import require_role
from fiscia.stripe_service import StripeService
from fiscia.usage_middleware import UsageGate, check_usage_credits
from fiscia.webhooks.stripe_handler import router as stripe_webhook_router

app = FastAPI(title="FiscIA Pro", version="0.4.0")
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(stripe_webhook_router)


class SearchIn(BaseModel):
    query: str = Field(..., min_length=1)


class CalcISIn(BaseModel):
    ca: Decimal = Field(..., ge=0)
    capital_pp: bool = False
    rf: Decimal = Field(default=Decimal("100000"), ge=0)
    user_id: int | None = None
    siren: str = "000000000"
    exercice_clos: date = Field(default_factory=date.today)


class LiasseIn(BaseModel):
    liasse: Liasse2058AInput
    ca: Decimal = Field(..., ge=0)
    capital_pp: bool = False
    user_id: int | None = None


class MereIn(BaseModel):
    pct_capital: Decimal = Field(default=Decimal("0"))
    annees_detention: Decimal = Field(default=Decimal("0"))
    nominatifs: bool | None = None
    nominatif: bool | None = None
    pleine_propriete: bool = False
    filiale_is: bool = False
    paradis_fiscal: bool = False
    dividende: Decimal | None = None
    dividende_brut: Decimal | None = None
    credit_impot: Decimal = Field(default=Decimal("0"))


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "billing": StripeService.billing_health()}


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    return {"status": "ok", "service": "fiscia-pro", "version": app.version}


@app.get("/health/db")
async def health_db() -> dict[str, Any]:
    db = await database_health_check()
    return {"database": db, "billing": StripeService.billing_health()}


@app.post("/search")
async def search(
    payload: SearchIn,
    current_user: User = Depends(require_role(Role.CLIENT.value)),
) -> dict[str, Any]:
    _ = current_user
    return {"results": cgi_search(payload.query), "disclaimer": MANDATORY_DISCLAIMER}


@app.post("/calc-is")
async def calc_is(
    payload: CalcISIn,
    request: Request,
    usage_gate: UsageGate = Depends(check_usage_credits),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict[str, Any]:
    current_user = usage_gate.user

    if payload.user_id is not None and payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-user writes are forbidden.")

    is_total, regime, tranche_15, tranche_25 = ISCalculator.calcul_is(
        rf=payload.rf,
        ca_ht=payload.ca,
        capital_75pct_pp=payload.capital_pp,
    )
    acompte = (is_total / Decimal("4")).quantize(Decimal("0.01")) if is_total > 0 else Decimal("0.00")

    response_text = f"Art. 219 CGI (LFI 2024)\nIS total: {is_total:.2f} EUR\n{MANDATORY_DISCLAIMER}"
    try:
        enforce_guardrails(
            response_text,
            {
                "pme_checked": True,
                "mere_conditions_present": True,
                "confidential": True,
                "module": "calc-is",
            },
        )
    except GuardrailError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        calc = await create_calculation(
            session,
            user_id=current_user.id,
            firm_id=current_user.firm_id,
            siren=payload.siren,
            exercice_clos=payload.exercice_clos,
            input_json=jsonable_encoder(payload.model_dump()),
            result_json=jsonable_encoder(
                {
                    "rf": payload.rf,
                    "regime": regime,
                    "tranche_15": tranche_15,
                    "tranche_25": tranche_25,
                    "is_total": is_total,
                    "acompte_trimestriel": acompte,
                }
            ),
        )
        await create_audit_log(
            session=session,
            user_id=current_user.id,
            firm_id=current_user.firm_id,
            action="calc_is",
            resource_type="liasse",
            resource_id=calc.id,
            details={
                "calculation_id": calc.id,
                "module": "calc_is",
                "firm_id": current_user.firm_id,
                "credit_usage": usage_gate.usage,
            },
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except CrudError as exc:
        raise HTTPException(status_code=503, detail=f"Database persistence failed: {exc}") from exc

    return {
        "calculation_id": calc.id,
        "rf": payload.rf,
        "regime": regime,
        "tranche_15": tranche_15,
        "tranche_25": tranche_25,
        "is_total": is_total,
        "acompte_trimestriel": acompte,
        "credit_usage": usage_gate.usage,
        "disclaimer": MANDATORY_DISCLAIMER,
    }


@app.post("/liasse")
async def liasse(
    payload: LiasseIn,
    request: Request,
    usage_gate: UsageGate = Depends(check_usage_credits),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict[str, Any]:
    current_user = usage_gate.user

    if payload.user_id is not None and payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-user writes are forbidden.")

    result = ISCalculator.process_liasse(payload.liasse, payload.ca, payload.capital_pp)
    response_text = f"Art. 219 CGI (LFI 2024)\nIS total: {result.is_total:.2f} EUR\n{MANDATORY_DISCLAIMER}"
    try:
        enforce_guardrails(
            response_text,
            {
                "pme_checked": True,
                "mere_conditions_present": True,
                "confidential": True,
                "module": "liasse",
            },
        )
    except GuardrailError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        calc = await create_calculation(
            session,
            user_id=current_user.id,
            firm_id=current_user.firm_id,
            siren=payload.liasse.siren,
            exercice_clos=payload.liasse.exercice_clos,
            input_json=jsonable_encoder(payload.liasse.model_dump(by_alias=False)),
            result_json=jsonable_encoder(result.model_dump()),
        )
        await create_audit_log(
            session=session,
            user_id=current_user.id,
            firm_id=current_user.firm_id,
            action="process_liasse",
            resource_type="liasse",
            resource_id=calc.id,
            details={
                "calculation_id": calc.id,
                "siren": payload.liasse.siren,
                "module": "liasse",
                "firm_id": current_user.firm_id,
                "credit_usage": usage_gate.usage,
            },
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except CrudError as exc:
        raise HTTPException(status_code=503, detail=f"Database persistence failed: {exc}") from exc

    return {
        "calculation_id": calc.id,
        "result": jsonable_encoder(result.model_dump()),
        "credit_usage": usage_gate.usage,
        "disclaimer": MANDATORY_DISCLAIMER,
    }


@app.post("/mere")
async def mere(
    payload: MereIn,
    current_user: User = Depends(require_role(Role.FISCALISTE.value)),
) -> dict[str, Any]:
    _ = current_user

    params = payload.model_dump(exclude_none=True)
    result = verifier_mere_filiale(params)
    answer = f"Art. 145 CGI (LFI 2024)\n{MANDATORY_DISCLAIMER}"
    try:
        enforce_guardrails(
            answer,
            {
                "pme_checked": True,
                "mere_conditions_present": bool(result.get("eligible", False)),
                "confidential": True,
                "module": "mere",
            },
        )
    except GuardrailError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"result": jsonable_encoder(result), "disclaimer": MANDATORY_DISCLAIMER}