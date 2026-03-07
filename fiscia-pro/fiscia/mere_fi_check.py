from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def _q(value: Decimal | float | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def verifier_mere_filiale(params: dict) -> dict:
    conds = {
        "c1_participation_5pct": Decimal(str(params.get("pct_capital", 0))) >= Decimal("5"),
        "c2_detention_2ans": Decimal(str(params.get("annees_detention", 0))) >= Decimal("2"),
        "c3_nominatifs": bool(params.get("nominatifs", params.get("nominatif", False))),
        "c4_pleine_propriete": bool(params.get("pleine_propriete", False)),
        "c5_filiale_is": bool(params.get("filiale_is", False)),
        "c6_hors_paradis": not bool(params.get("paradis_fiscal", False)),
    }
    eligible = all(conds.values())

    if eligible:
        dividende = _q(params.get("dividende", params.get("dividende_brut", 0)))
        credit_impot = _q(params.get("credit_impot", 0))
        qp5 = _q((dividende + credit_impot) * Decimal("0.05"))
        return {
            "eligible": True,
            "deduction_WV": dividende,
            "reintegration_WN_qp5": qp5,
            "impact_rf_net": _q(-dividende + qp5),
            "base_legale": "Art. 145 et 216 CGI (LFI 2024)",
            "conditions": conds,
        }

    return {
        "eligible": False,
        "failed_conditions": [k for k, v in conds.items() if not v],
        "base_legale": "Art. 145 CGI (LFI 2024)",
        "conditions": conds,
    }

