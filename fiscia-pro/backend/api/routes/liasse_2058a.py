"""Routes for 2058-A fiscal computation workflows."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..middleware import AuthUser, audit_log, get_current_user
from ...services import FiscalContext, ISCalculator, LLMRouter

router = APIRouter(prefix="/liasse", tags=["liasse_2058a"])

FISCAL_DISCLAIMER = (
    "Reponse indicative. Toute decision fiscale engageante necessite une analyse personnalisee "
    "par un professionnel qualifie."
)


class Liasse2058AInput(BaseModel):
    siren: str | None = None
    ca_ht: Decimal = Decimal("0")
    capital_pme: bool = False

    WA_benefice_comptable: Decimal = Field(default=Decimal("0"))
    WQ_perte_comptable: Decimal = Field(default=Decimal("0"))
    WB_remuneration_exploitant: Decimal = Field(default=Decimal("0"))
    WC_avantages_personnels: Decimal = Field(default=Decimal("0"))
    WD_amortissements_excedentaires: Decimal = Field(default=Decimal("0"))
    WE_charges_somptuaires: Decimal = Field(default=Decimal("0"))
    WF_taxe_vehicules_societe: Decimal = Field(default=Decimal("0"))
    WG_amendes_penalites: Decimal = Field(default=Decimal("0"))
    WI_is_et_ifa: Decimal = Field(default=Decimal("0"))
    WJ_pv_exercices_anterieurs: Decimal = Field(default=Decimal("0"))
    WK_provisions_non_deductibles: Decimal = Field(default=Decimal("0"))
    K7_qp_pertes_soc_personnes_gie: Decimal = Field(default=Decimal("0"))
    WL_benefices_soc_personnes_gie: Decimal = Field(default=Decimal("0"))
    WM_interets_excedentaires: Decimal = Field(default=Decimal("0"))
    WN_reintegrations_diverses: Decimal = Field(default=Decimal("0"))
    WO_ecarts_opcvm_reintegration: Decimal = Field(default=Decimal("0"))
    L7_resultats_art209B: Decimal = Field(default=Decimal("0"))

    WR_mv_lt_taux_15_8_0: Decimal = Field(default=Decimal("0"))
    L2_pv_lt_imposees_15pct: Decimal = Field(default=Decimal("0"))
    L3_pv_lt_imputees_mv_ant: Decimal = Field(default=Decimal("0"))
    L4_pv_lt_imposees_8pct: Decimal = Field(default=Decimal("0"))
    L5_pv_lt_imputees_deficits: Decimal = Field(default=Decimal("0"))
    WS_pv_ct_imposition_differee: Decimal = Field(default=Decimal("0"))
    WT_pv_regime_fusions: Decimal = Field(default=Decimal("0"))
    WU_ecarts_opcvm_deduction: Decimal = Field(default=Decimal("0"))
    WV_regime_mere_filiale: Decimal = Field(default=Decimal("0"))
    L6_produit_net_qp_frais: Decimal = Field(default=Decimal("0"))
    L8_qp_5pct_pv_taux_zero: Decimal = Field(default=Decimal("0"))
    WW_zones_entreprises_exonerees: Decimal = Field(default=Decimal("0"))
    XB_deductions_diverses: Decimal = Field(default=Decimal("0"))
    WZ_majoration_amortissement: Decimal = Field(default=Decimal("0"))
    XA_investissements_outremer: Decimal = Field(default=Decimal("0"))

    XD_entreprises_nouvelles_44sexies: Decimal = Field(default=Decimal("0"))
    XF_reprise_difficultes_44septies: Decimal = Field(default=Decimal("0"))
    XS_corse_208quatera: Decimal = Field(default=Decimal("0"))
    XG_zf_corse_44decies: Decimal = Field(default=Decimal("0"))
    XJ_zfu_44octies_44octiesA: Decimal = Field(default=Decimal("0"))
    XL_jei_44sexiesA: Decimal = Field(default=Decimal("0"))
    XO_pole_competitivite_44undecies: Decimal = Field(default=Decimal("0"))
    XH_siic_208c: Decimal = Field(default=Decimal("0"))
    L9_abattements_exonerations: Decimal = Field(default=Decimal("0"))

    ZL_deficit_reporte_arriere: Decimal = Field(default=Decimal("0"))
    XI_deficits_anterieurs_imputes: Decimal = Field(default=Decimal("0"))


@router.post("/calculer")
async def calculer_liasse(
    liasse_data: Liasse2058AInput,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
) -> dict:
    """
    Calcule le RF a partir des donnees 2058-A saisies
    + detection IA des anomalies + suggestions d'optimisation.
    """
    calc = ISCalculator()
    llm = LLMRouter()

    rf_result = calc.calculer_rf(liasse_data)
    is_result = calc.calculer_is(
        rf=rf_result.rf_net,
        ca_ht=liasse_data.ca_ht,
        capital_75pct_pp=liasse_data.capital_pme,
    )
    anomalies = await llm.route_query(
        query=f"Verifie cette liasse 2058-A : {rf_result.dict()}",
        context=FiscalContext(module="liasse_2058a"),
        is_confidentiel=True,
    )

    await audit_log(
        user_id=str(current_user.id),
        action="calcul_liasse",
        siren=liasse_data.siren,
        module="liasse_2058a",
    )

    return {
        "rf_result": rf_result.dict(),
        "is_result": is_result.dict(),
        "anomalies_ia": anomalies.suggestions,
        "llm_provider": anomalies.provider,
        "disclaimer": FISCAL_DISCLAIMER,
        "lignes_2058a_calculees": {
            "XR_total_I": float(rf_result.xr_total_i),
            "ZY_total_II": float(rf_result.zy_total_ii),
            "ZI_rf_brut": float(rf_result.rf_brut),
            "XN_benefice": float(rf_result.xn_benefice),
            "XO_deficit": float(rf_result.xo_deficit),
        },
    }
