"""
Moteur de calcul fiscal — Formulaire 2058-A
Résultat Fiscal = Résultat Comptable (WA) + Réintégrations (WS) - Déductions (WT)
"""

from src.database.models import Form2058A


REINTEGRATION_FIELDS = [
    "wb_remuneration_exploitant",
    "wc_part_deductible",
    "wd_avantages_personnels",
    "we_amortissements_excessifs",
    "wf_impot_societes",
    "wg_provisions_non_deductibles",
    "wh_amendes_penalites",
    "wi_charges_somptuaires",
    "wj_interets_excessifs",
    "wk_charges_payer_non_deduct",
    "wl_autres_reintegrations",
]

DEDUCTION_FIELDS = [
    "wm_quote_part_gie",
    "wn_produits_participation",
    "wo_plus_values_lt",
    "wp_loyers_excessifs",
    "wq_reprises_provisions",
    "wr_autres_deductions",
]


def calculate_2058a(form: Form2058A) -> dict:
    """Calcule les totaux et le résultat fiscal à partir des lignes du formulaire."""
    total_reintegrations = sum(
        getattr(form, field) or 0.0 for field in REINTEGRATION_FIELDS
    )
    total_deductions = sum(
        getattr(form, field) or 0.0 for field in DEDUCTION_FIELDS
    )
    wa = form.wa_resultat_comptable or 0.0
    resultat_fiscal = wa + total_reintegrations - total_deductions

    return {
        "ws_total_reintegrations": round(total_reintegrations, 2),
        "wt_total_deductions": round(total_deductions, 2),
        "wu_resultat_fiscal": round(resultat_fiscal, 2),
        "is_benefice": resultat_fiscal >= 0,
    }


def calculate_is(resultat_fiscal: float, is_pme: bool = True) -> dict:
    """
    Calcule l'impôt sur les sociétés (IS) à partir du résultat fiscal.
    Taux 2024 :
      - PME : 15% jusqu'à 42 500 €, puis 25%
      - Normal : 25% sur la totalité
    """
    if resultat_fiscal <= 0:
        return {"is_du": 0.0, "taux_effectif": 0.0}

    if is_pme and resultat_fiscal <= 42_500:
        is_du = resultat_fiscal * 0.15
    elif is_pme:
        is_du = 42_500 * 0.15 + (resultat_fiscal - 42_500) * 0.25
    else:
        is_du = resultat_fiscal * 0.25

    taux_effectif = (is_du / resultat_fiscal) * 100 if resultat_fiscal > 0 else 0.0

    return {
        "is_du": round(is_du, 2),
        "taux_effectif": round(taux_effectif, 2),
    }
