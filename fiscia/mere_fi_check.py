"""
Verificateur du regime des societes meres et filiales - Art. 145 CGI
6 conditions cumulatives.
"""
from decimal import Decimal, ROUND_HALF_UP


def verifier_mere_filiale(params: dict) -> dict:
    """
    Verifie les 6 conditions cumulatives de l'Art. 145 CGI.

    params attendus:
        pct_capital (float)      - % de detention du capital de la filiale
        annees_detention (int)   - nombre d'annees de detention des titres
        nominatifs (bool)        - titres nominatifs ?
        pleine_propriete (bool)  - pleine propriete (non demembres) ?
        filiale_is (bool)        - filiale soumise IS ?
        paradis_fiscal (bool)    - filiale dans un ETNC ?
        dividende (float)        - montant du dividende brut recu
        credit_impot (float)     - credit d'impot associe
    """
    conditions = {
        "c1_seuil_5pct": params.get("pct_capital", 0) >= 5,
        "c2_detention_2ans": params.get("annees_detention", 0) >= 2,
        "c3_nominatifs": bool(params.get("nominatifs", False)),
        "c4_pleine_propriete": bool(params.get("pleine_propriete", False)),
        "c5_filiale_IS": bool(params.get("filiale_is", False)),
        "c6_hors_paradis": not bool(params.get("paradis_fiscal", False)),
    }

    eligible = all(conditions.values())

    if eligible:
        div = Decimal(str(params.get("dividende", 0)))
        ci = Decimal(str(params.get("credit_impot", 0)))
        qp_5pct = ((div + ci) * Decimal("0.05")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        impact = (-div + qp_5pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "eligible": True,
            "conditions": conditions,
            "deduction_WV": float(div),
            "reintegration_WN_qp5": float(qp_5pct),
            "impact_rf_net": float(impact),
            "base_legale": "Art. 145 et 216 CGI",
            "disclaimer": (
                "Reponse indicative. Toute decision fiscale engageante "
                "necessite l'analyse personnalisee d'un professionnel qualifie."
            ),
        }

    failed = [k for k, v in conditions.items() if not v]
    return {
        "eligible": False,
        "conditions": conditions,
        "conditions_echouees": failed,
        "consequence": "Dividendes integralement imposables a l'IS au taux applicable (25% ou 15% PME)",
        "alerte": "REGIME MERE-FILIALE INAPPLICABLE",
        "disclaimer": (
            "Reponse indicative. Toute decision fiscale engageante "
            "necessite l'analyse personnalisee d'un professionnel qualifie."
        ),
    }
