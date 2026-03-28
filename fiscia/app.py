"""
FiscIA Pro - FastAPI service.
"""
import logging
from decimal import Decimal
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from fiscia.cgi_search import search as cgi_search
from fiscia.crud import (
    create_liasse_calculation,
    delete_liasse_calculation,
    get_liasse_calculation,
    list_liasse_calculations,
)
from fiscia.crud_async import (
    async_create_liasse_calculation,
    async_delete_liasse_calculation,
    async_get_liasse_calculation,
    async_list_audit_logs,
    async_list_liasse_calculations,
)
from fiscia.database import check_database_health, create_all_tables, get_db
from fiscia.database_async import AsyncSession as AsyncDBSession
from fiscia.database_async import check_async_database_health, get_async_db
from fiscia.guardrails import GuardrailError, enforce_guardrails
from fiscia.health import check_full_health
from fiscia.is_calculator import DISCLAIMER, ISCalculator
from fiscia.logging_config import setup_logging
from fiscia.mere_fi_check import verifier_mere_filiale
from fiscia.metrics import (
    CGI_SEARCHES,
    IS_CALCULATIONS,
    LIASSE_CALCULATIONS,
    MERE_FILIALE_CHECKS,
)
from fiscia.models import Liasse2058AInput, Liasse2058BCInput, Liasse2058BCResult
from fiscia.monitoring import ObservabilityMiddleware
from fiscia.auth_endpoints import router as auth_router
from fiscia.dependencies import CurrentUser, get_current_user, require_role
from fiscia.gdpr import router as gdpr_router
from fiscia.billing_endpoints import router as billing_router
from fiscia.webhooks.stripe_handler import router as webhook_router
from fiscia.ollama_client import (
    OLLAMA_MODEL,
    OllamaError,
    generate as ollama_generate,
    check_available as ollama_available,
)

logger = logging.getLogger("fiscia.app")

LOCAL_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3100",
    "http://127.0.0.1:3100",
    "http://localhost:3101",
    "http://127.0.0.1:3101",
]

app = FastAPI(title="FiscIA Pro - API", version="3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=LOCAL_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ObservabilityMiddleware)
app.include_router(auth_router)
app.include_router(gdpr_router)
app.include_router(billing_router)
app.include_router(webhook_router)
calculator = ISCalculator()


@app.on_event("startup")
def on_startup():
    """Create tables and initialize logging on startup."""
    setup_logging()
    create_all_tables()
    logger.info("FiscIA Pro started")


# --- Request schemas ---

class SearchRequest(BaseModel):
    query: str


class CalcISRequest(BaseModel):
    ca: float
    capital_pp: bool = False


class LiasseRequest(BaseModel):
    liasse: Liasse2058AInput
    ca: float
    capital_pp: bool = False


class Liasse2058BCRequest(BaseModel):
    liasse: Liasse2058AInput
    ca: float
    capital_pp: bool = False
    annexes: Liasse2058BCInput = Field(default_factory=Liasse2058BCInput)


class MereRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pct_capital: float
    annees_detention: int
    nominatifs: bool = Field(default=False, alias="nominatif")
    pleine_propriete: bool = False
    filiale_is: bool = False
    paradis_fiscal: bool = False
    dividende: float = Field(default=0, alias="dividende_brut")
    credit_impot: float = 0


class AIExplainRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=5000, description="Question fiscale")
    mode: str = Field(default="general", pattern="^(is|liasse|mere|general)$")
    temperature: float = Field(default=0.05, ge=0.0, le=1.0)


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/database")
def health_database():
    result = check_database_health()
    if result["status"] != "ok":
        raise HTTPException(status_code=503, detail=result)
    return result


@app.get("/health/full")
async def health_full(response: Response):
    """Aggregated health check: database + Ollama + app status."""
    result = await check_full_health()
    if result["status"] == "unhealthy":
        response.status_code = 503
    return result


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics():
    """Prometheus scrape endpoint."""
    return PlainTextResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/search")
def search_cgi(req: SearchRequest):
    CGI_SEARCHES.inc()
    results = cgi_search(req.query, top_n=5)
    if not results:
        raise HTTPException(status_code=404, detail="Aucun article trouve.")
    return {"results": results, "disclaimer": DISCLAIMER}


@app.post("/calc-is")
def calc_is(req: CalcISRequest):
    rf = Decimal("100000")
    is_total, regime, t15, t25 = calculator.calcul_is(
        rf, Decimal(str(req.ca)), req.capital_pp
    )
    IS_CALCULATIONS.labels(regime=regime).inc()
    acompte = (is_total / 4).quantize(Decimal("0.01"))
    return {
        "rf": float(rf),
        "regime": regime,
        "tranche_15pct": float(t15),
        "tranche_25pct": float(t25),
        "is_total": float(is_total),
        "acompte_trimestriel": float(acompte),
        "disclaimer": DISCLAIMER,
    }


@app.post("/liasse")
def process_liasse(
    req: LiasseRequest,
    save: bool = Query(False, description="Save calculation to database"),
    user_id: Optional[str] = Query(None, description="User ID for saved calculations"),
    db: Session = Depends(get_db),
):
    result = calculator.process_liasse(
        req.liasse, Decimal(str(req.ca)), req.capital_pp
    )

    output_text = (
        f"RF brut: {result.rf_brut} EUR, IS TOTAL: {result.is_total} EUR. "
        f"Regime (LFI 2024): {result.regime}. "
        f"Disclaimer: {DISCLAIMER}"
    )

    context = {
        "pme_checked": True,
        "confidential": True,
        "module": "liasse",
        "mere_conditions_present": float(req.liasse.wv_regime_mere_filiale) > 0,
    }
    try:
        enforce_guardrails(output_text, context)
    except GuardrailError as e:
        raise HTTPException(status_code=422, detail=str(e))

    LIASSE_CALCULATIONS.labels(regime=result.regime, saved=str(save).lower()).inc()
    response = {
        "rf_brut": float(result.rf_brut),
        "rf_net": float(result.rf_net),
        "is_total": float(result.is_total),
        "regime": result.regime,
        "acompte_trimestriel": float(result.acompte_trimestriel),
        "details": {k: float(v) for k, v in result.details.items()},
        "meta": {
            "ca": float(req.ca),
            "capital_pp": req.capital_pp,
        },
        "disclaimer": DISCLAIMER,
    }

    if save:
        record = create_liasse_calculation(
            db=db,
            user_id=user_id,
            siren=req.liasse.siren,
            exercice_clos=req.liasse.exercice_clos,
            input_data=req.liasse.model_dump(mode="json"),
            result_data=response,
        )
        response["saved_id"] = record.id

    return response


@app.post("/mere")
def check_mere_filiale(req: MereRequest):
    params = {
        "pct_capital": req.pct_capital,
        "annees_detention": req.annees_detention,
        "nominatifs": req.nominatifs,
        "pleine_propriete": req.pleine_propriete,
        "filiale_is": req.filiale_is,
        "paradis_fiscal": req.paradis_fiscal,
        "dividende": req.dividende,
        "credit_impot": req.credit_impot,
    }
    result = verifier_mere_filiale(params)
    MERE_FILIALE_CHECKS.labels(eligible=str(result["eligible"]).lower()).inc()

    output_text = (
        f"Art. 145 CGI (LFI 2024). Eligible: {result['eligible']}. "
        f"Disclaimer: {DISCLAIMER}"
    )
    context = {
        "pme_checked": True,
        "confidential": True,
        "module": "mere",
        "mere_conditions_present": result["eligible"],
    }
    try:
        enforce_guardrails(output_text, context)
    except GuardrailError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return result


# --- Persistence endpoints ---

@app.get("/liasse/saved")
def list_saved_liasses(
    user_id: Optional[str] = Query(None),
    siren: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List saved liasse calculations."""
    records = list_liasse_calculations(db, user_id=user_id, siren=siren, skip=skip, limit=limit)
    return {
        "count": len(records),
        "results": [
            {
                "id": r.id,
                "siren": r.siren,
                "exercice_clos": r.exercice_clos,
                "rf_brut": r.rf_brut,
                "rf_net": r.rf_net,
                "is_total": r.is_total,
                "regime": r.regime,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
        "disclaimer": DISCLAIMER,
    }


@app.get("/liasse/saved/{liasse_id}")
def get_saved_liasse(
    liasse_id: str,
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieve a saved liasse calculation by ID."""
    record = get_liasse_calculation(db, liasse_id, user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Calcul non trouve.")
    return {
        "id": record.id,
        "user_id": record.user_id,
        "siren": record.siren,
        "exercice_clos": record.exercice_clos,
        "input_data": record.input_data,
        "result_data": record.result_data,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        "disclaimer": DISCLAIMER,
    }


@app.delete("/liasse/saved/{liasse_id}")
def delete_saved_liasse(
    liasse_id: str,
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Delete a saved liasse calculation."""
    deleted = delete_liasse_calculation(db, liasse_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Calcul non trouve.")
    return {"deleted": True, "id": liasse_id, "disclaimer": DISCLAIMER}


# --- Async v2 endpoints ---

@app.get("/v2/health/database")
async def health_database_v2():
    result = await check_async_database_health()
    if result["status"] != "ok":
        raise HTTPException(status_code=503, detail=result)
    return result


@app.post("/v2/liasse")
async def process_liasse_v2(
    req: LiasseRequest,
    save: bool = Query(False, description="Save calculation to database"),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncDBSession = Depends(get_async_db),
):
    result = calculator.process_liasse(
        req.liasse, Decimal(str(req.ca)), req.capital_pp
    )

    output_text = (
        f"RF brut: {result.rf_brut} EUR, IS TOTAL: {result.is_total} EUR. "
        f"Regime (LFI 2024): {result.regime}. "
        f"Disclaimer: {DISCLAIMER}"
    )
    context = {
        "pme_checked": True,
        "confidential": True,
        "module": "liasse",
        "mere_conditions_present": float(req.liasse.wv_regime_mere_filiale) > 0,
    }
    try:
        enforce_guardrails(output_text, context)
    except GuardrailError as e:
        raise HTTPException(status_code=422, detail=str(e))

    LIASSE_CALCULATIONS.labels(regime=result.regime, saved=str(save).lower()).inc()
    response = {
        "rf_brut": float(result.rf_brut),
        "rf_net": float(result.rf_net),
        "is_total": float(result.is_total),
        "regime": result.regime,
        "acompte_trimestriel": float(result.acompte_trimestriel),
        "details": {k: float(v) for k, v in result.details.items()},
        "meta": {
            "ca": float(req.ca),
            "capital_pp": req.capital_pp,
        },
        "disclaimer": DISCLAIMER,
    }

    if save:
        record = await async_create_liasse_calculation(
            db=db,
            user_id=user.id,
            siren=req.liasse.siren,
            exercice_clos=req.liasse.exercice_clos,
            input_data=req.liasse.model_dump(mode="json"),
            result_data=response,
        )
        response["saved_id"] = record.id

    return response


@app.post("/v2/liasse/2058-bc")
async def prepare_liasse_2058bc_v2(
    req: Liasse2058BCRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Prepare working drafts for 2058-B and 2058-C based on 2058-A inputs and IS settings."""
    result = calculator.process_liasse(
        req.liasse, Decimal(str(req.ca)), req.capital_pp
    )
    annexes = req.annexes

    rf_brut = Decimal(str(result.rf_brut))
    rf_positive = max(rf_brut, Decimal("0"))
    deficits_ouverture = Decimal(str(annexes.deficits_reportables_ouverture))
    deficits_imputes = min(deficits_ouverture, rf_positive)
    deficit_exercice = max(-rf_brut, Decimal("0"))
    deficits_cloture = deficits_ouverture - deficits_imputes + deficit_exercice

    moins_values_ouverture = Decimal(str(annexes.moins_values_lt_ouverture))
    moins_values_imputees = min(
        Decimal(str(annexes.moins_values_lt_imputees)), moins_values_ouverture
    )
    moins_values_cloture = moins_values_ouverture - moins_values_imputees

    base_imposable_apres_reports = max(rf_positive - deficits_imputes, Decimal("0"))
    is_total, regime, tranche_15, tranche_25 = calculator.calcul_is(
        base_imposable_apres_reports,
        Decimal(str(req.ca)),
        req.capital_pp,
    )

    contribution_sociale = Decimal(str(annexes.contribution_sociale))
    regularisations = Decimal(str(annexes.regularisations))
    acomptes_verses = Decimal(str(annexes.acomptes_verses))
    credits_impot = Decimal(str(annexes.credits_impot))

    total_du = is_total + contribution_sociale + regularisations
    total_imputations = acomptes_verses + credits_impot
    solde_a_payer = max(total_du - total_imputations, Decimal("0"))
    creance_restante = max(total_imputations - total_du, Decimal("0"))

    output_text = (
        f"Preparation 2058-B/C - RF brut: {rf_brut} EUR, "
        f"base imposable apres reports: {base_imposable_apres_reports} EUR, "
        f"IS total: {is_total} EUR. Disclaimer: {DISCLAIMER}"
    )
    context = {
        "pme_checked": True,
        "confidential": True,
        "module": "liasse",
        "mere_conditions_present": float(req.liasse.wv_regime_mere_filiale) > 0,
    }
    try:
        enforce_guardrails(output_text, context)
    except GuardrailError as e:
        raise HTTPException(status_code=422, detail=str(e))

    response = Liasse2058BCResult(
        tableau_2058b={
            "resultat_fiscal_brut": rf_brut,
            "deficits_reportables_ouverture": deficits_ouverture,
            "deficits_imputes_exercice": deficits_imputes,
            "deficit_exercice": deficit_exercice,
            "deficits_reportables_cloture": deficits_cloture,
            "moins_values_lt_ouverture": moins_values_ouverture,
            "moins_values_lt_imputees": moins_values_imputees,
            "moins_values_lt_cloture": moins_values_cloture,
            "base_imposable_apres_reports": base_imposable_apres_reports,
        },
        tableau_2058c={
            "base_imposable_is": base_imposable_apres_reports,
            "tranche_15pct": tranche_15,
            "tranche_25pct": tranche_25,
            "is_total": is_total,
            "contribution_sociale": contribution_sociale,
            "regularisations": regularisations,
            "total_du": total_du,
            "acomptes_verses": acomptes_verses,
            "credits_impot": credits_impot,
            "total_imputations": total_imputations,
            "solde_a_payer": solde_a_payer,
            "creance_restante": creance_restante,
        },
        regime=regime,
        notes=[
            "Brouillon de preparation 2058-B / 2058-C a revoir avant depot EDI.",
            "Les deficits reportables et les moins-values long terme sont repris des donnees saisies dans le module.",
            "Les acomptes, credits d'impot et regularisations restent a confirmer avec le dossier de cloture.",
        ],
        disclaimer=DISCLAIMER,
    )
    payload = response.model_dump(mode="json")
    payload["tableau_2058b"] = {
        key: float(value) for key, value in response.tableau_2058b.items()
    }
    payload["tableau_2058c"] = {
        key: float(value) for key, value in response.tableau_2058c.items()
    }
    return payload


@app.get("/v2/liasse/saved")
async def list_saved_liasses_v2(
    siren: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncDBSession = Depends(get_async_db),
):
    records = await async_list_liasse_calculations(db, user_id=user.id, siren=siren, skip=skip, limit=limit)
    return {
        "count": len(records),
        "results": [
            {
                "id": r.id,
                "siren": r.siren,
                "exercice_clos": r.exercice_clos,
                "rf_brut": r.rf_brut,
                "rf_net": r.rf_net,
                "is_total": r.is_total,
                "regime": r.regime,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
        "disclaimer": DISCLAIMER,
    }


@app.get("/v2/liasse/saved/{liasse_id}")
async def get_saved_liasse_v2(
    liasse_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncDBSession = Depends(get_async_db),
):
    record = await async_get_liasse_calculation(db, liasse_id, user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="Calcul non trouve.")
    return {
        "id": record.id,
        "user_id": record.user_id,
        "siren": record.siren,
        "exercice_clos": record.exercice_clos,
        "input_data": record.input_data,
        "result_data": record.result_data,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        "disclaimer": DISCLAIMER,
    }


@app.delete("/v2/liasse/saved/{liasse_id}")
async def delete_saved_liasse_v2(
    liasse_id: str,
    user: CurrentUser = Depends(require_role("fiscaliste")),
    db: AsyncDBSession = Depends(get_async_db),
):
    deleted = await async_delete_liasse_calculation(db, liasse_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Calcul non trouve.")
    return {"deleted": True, "id": liasse_id, "disclaimer": DISCLAIMER}


@app.get("/audit-logs")
async def list_audit_logs(
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    admin: CurrentUser = Depends(require_role("admin")),
    db: AsyncDBSession = Depends(get_async_db),
):
    logs = await async_list_audit_logs(db, user_id=user_id, action=action, skip=skip, limit=limit)
    return {
        "count": len(logs),
        "results": [
            {
                "id": log_entry.id,
                "user_id": log_entry.user_id,
                "action": log_entry.action,
                "module": log_entry.module,
                "siren": log_entry.siren,
                "detail": log_entry.detail,
                "ip_address": log_entry.ip_address,
                "created_at": log_entry.created_at.isoformat() if log_entry.created_at else None,
            }
            for log_entry in logs
        ],
    }


# --- AI-assisted reasoning endpoints (Ollama) ---

@app.get("/v2/ai/status")
async def ai_status():
    """Check if AI reasoning (Ollama) is available."""
    available = await ollama_available()
    return {"available": available, "model": OLLAMA_MODEL}


@app.post("/v2/ai/explain")
async def ai_explain(
    req: AIExplainRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """General fiscal AI reasoning. Send a free-form question about IS, 2058-A, or Art. 145."""
    try:
        result = await ollama_generate(
            prompt=req.prompt,
            mode=req.mode,
            temperature=req.temperature,
        )
    except OllamaError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return result


@app.post("/v2/ai/explain-is")
async def ai_explain_is(
    req: CalcISRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """AI-assisted IS calculation explanation. Sends structured data to Ollama for detailed reasoning."""
    prompt = (
        f"Calcule l'IS pour une entreprise avec:\n"
        f"- CA HT: {req.ca:,.0f} EUR\n"
        f"- Capital detenu >= 75% par personnes physiques: {'OUI' if req.capital_pp else 'NON'}\n"
        f"- Resultat fiscal: 100 000 EUR\n\n"
        f"Donne le detail des tranches, l'IS total du, et les acomptes trimestriels."
    )
    try:
        result = await ollama_generate(prompt=prompt, mode="is")
    except OllamaError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return result


@app.post("/v2/ai/explain-liasse")
async def ai_explain_liasse(
    req: LiasseRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """AI-assisted liasse 2058-A explanation. Sends liasse data to Ollama for line-by-line analysis."""
    liasse = req.liasse
    prompt = (
        f"Analyse la liasse 2058-A suivante:\n"
        f"- SIREN: {liasse.siren}, Exercice: {liasse.exercice_clos}\n"
        f"- Benefice comptable (ligne XN): {liasse.benefice_comptable} EUR\n"
        f"- IS comptabilise (WI): {liasse.wi_is_comptabilise} EUR\n"
        f"- Amendes/penalites (WG): {liasse.wg_amendes_penalites} EUR\n"
        f"- Interets excedentaires CC (WM): {liasse.wm_interets_excedentaires} EUR\n"
        f"- Regime mere-filiale WV: {liasse.wv_regime_mere_filiale} EUR\n"
        f"- CA HT: {req.ca:,.0f} EUR\n"
        f"- Capital PP: {'OUI' if req.capital_pp else 'NON'}\n\n"
        f"Pour chaque ligne, indique le sens (reintegration/deduction), "
        f"l'article CGI, et l'impact sur le RF. Puis calcule l'IS total."
    )
    try:
        result = await ollama_generate(prompt=prompt, mode="liasse")
    except OllamaError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return result


@app.post("/v2/ai/explain-mere")
async def ai_explain_mere(
    req: MereRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """AI-assisted Art. 145 mere-filiale verification with detailed reasoning."""
    prompt = (
        f"Verifie l'eligibilite au regime mere-filiale Art. 145 CGI:\n"
        f"- Participation au capital: {req.pct_capital}%\n"
        f"- Duree de detention: {req.annees_detention} ans\n"
        f"- Titres nominatifs: {'OUI' if req.nominatifs else 'NON'}\n"
        f"- Pleine propriete: {'OUI' if req.pleine_propriete else 'NON'}\n"
        f"- Filiale soumise IS: {'OUI' if req.filiale_is else 'NON'}\n"
        f"- Paradis fiscal/ETNC: {'OUI' if req.paradis_fiscal else 'NON'}\n"
        f"- Dividendes bruts: {req.dividende:,.0f} EUR\n"
        f"- Credit d'impot: {req.credit_impot:,.0f} EUR\n\n"
        f"Verifie les 6 conditions une par une. Si eligible, calcule "
        f"la deduction WV, la reintegration WN (QP 5%), et l'impact RF net."
    )
    try:
        result = await ollama_generate(prompt=prompt, mode="mere")
    except OllamaError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return result
