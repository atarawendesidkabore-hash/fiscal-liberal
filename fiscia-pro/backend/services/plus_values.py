"""Long/short-term capital gains engine for IS use-cases."""

from __future__ import annotations

from decimal import Decimal

from .is_calculator import money


class PlusValuesService:
    """Compute PV LT treatment including mandatory L8 quote-part."""

    QP_PV_LT_TITRES_PARTICIPATION = Decimal("0.12")

    def calculer_pv_lt_titres_participation(
        self,
        plus_value_brute: Decimal,
        moins_values_lt_imputables: Decimal = Decimal("0"),
    ) -> dict[str, float]:
        pv = Decimal(str(plus_value_brute))
        mv = max(Decimal(str(moins_values_lt_imputables)), Decimal("0"))
        base_nette = max(pv - mv, Decimal("0"))
        qp_l8 = base_nette * self.QP_PV_LT_TITRES_PARTICIPATION

        return {
            "pv_brute": float(money(pv)),
            "mv_lt_imputees": float(money(mv)),
            "base_taux_zero": float(money(base_nette)),
            "reintegration_l8_qp12pct": float(money(qp_l8)),
            "commentaire": "PV LT titres de participation a 0% avec QP 12% a reintegrer ligne L8",
        }

