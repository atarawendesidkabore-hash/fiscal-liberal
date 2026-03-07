"""Core IS calculator (Art. 219 CGI) and 2058-A fiscal result engine."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


EURO_2 = Decimal("0.01")


def d(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def money(value: Decimal) -> Decimal:
    return value.quantize(EURO_2, rounding=ROUND_HALF_UP)


@dataclass(slots=True)
class ResultatFiscal:
    rc: Decimal
    reintegrations: Decimal
    deductions: Decimal
    rf_brut: Decimal
    rf_net: Decimal
    xr_total_i: Decimal
    zy_total_ii: Decimal
    zi_rf_avant_regimes: Decimal
    xn_benefice: Decimal
    xo_deficit: Decimal

    def dict(self) -> dict[str, float]:
        return {k: float(v) for k, v in asdict(self).items()}


@dataclass(slots=True)
class CalculIS:
    rf: Decimal
    pme_eligible: bool
    regime: str
    tranche_15pct: Decimal
    tranche_25pct: Decimal
    is_total: Decimal
    acompte_trimestriel: Decimal

    def dict(self) -> dict[str, float | bool | str]:
        payload: dict[str, float | bool | str] = {
            "rf": float(self.rf),
            "pme_eligible": self.pme_eligible,
            "regime": self.regime,
            "tranche_15pct": float(self.tranche_15pct),
            "tranche_25pct": float(self.tranche_25pct),
            "is_total": float(self.is_total),
            "acompte_trimestriel": float(self.acompte_trimestriel),
        }
        return payload


def sum_abattements(liasse: Any) -> Decimal:
    fields = [
        "XD_entreprises_nouvelles_44sexies",
        "XF_reprise_difficultes_44septies",
        "XS_corse_208quatera",
        "XG_zf_corse_44decies",
        "XJ_zfu_44octies_44octiesA",
        "XL_jei_44sexiesA",
        "XO_pole_competitivite_44undecies",
        "XH_siic_208c",
        "L9_abattements_exonerations",
    ]
    return sum((d(getattr(liasse, f, 0)) for f in fields), Decimal("0"))


class ISCalculator:
    """
    Moteur de calcul IS conforme Art. 219 CGI.
    PME taux réduit: Art. 219-I-b CGI.
    """

    TAUX_NORMAL = Decimal("0.25")
    TAUX_REDUIT_PME = Decimal("0.15")
    SEUIL_TAUX_REDUIT = Decimal("42500")
    PLAFOND_CA_PME = Decimal("10000000")

    def calculer_rf(self, liasse: Any) -> ResultatFiscal:
        """Formule DGFiP: RF = RC + Σ Réintégrations - Σ Déductions."""
        rc = d(getattr(liasse, "WA_benefice_comptable", 0)) - d(getattr(liasse, "WQ_perte_comptable", 0))

        reintegrations = sum(
            (
                d(getattr(liasse, "WB_remuneration_exploitant", 0)),
                d(getattr(liasse, "WC_avantages_personnels", 0)),
                d(getattr(liasse, "WD_amortissements_excedentaires", 0)),
                d(getattr(liasse, "WE_charges_somptuaires", 0)),
                d(getattr(liasse, "WF_taxe_vehicules_societe", 0)),
                d(getattr(liasse, "WG_amendes_penalites", 0)),
                d(getattr(liasse, "WI_is_et_ifa", 0)),
                d(getattr(liasse, "WJ_pv_exercices_anterieurs", 0)),
                d(getattr(liasse, "WK_provisions_non_deductibles", 0)),
                d(getattr(liasse, "K7_qp_pertes_soc_personnes_gie", 0)),
                d(getattr(liasse, "WL_benefices_soc_personnes_gie", 0)),
                d(getattr(liasse, "WM_interets_excedentaires", 0)),
                d(getattr(liasse, "WN_reintegrations_diverses", 0)),
                d(getattr(liasse, "WO_ecarts_opcvm_reintegration", 0)),
                d(getattr(liasse, "L7_resultats_art209B", 0)),
            ),
            Decimal("0"),
        )

        deductions = sum(
            (
                d(getattr(liasse, "WR_mv_lt_taux_15_8_0", 0)),
                d(getattr(liasse, "L2_pv_lt_imposees_15pct", 0)),
                d(getattr(liasse, "L3_pv_lt_imputees_mv_ant", 0)),
                d(getattr(liasse, "L4_pv_lt_imposees_8pct", 0)),
                d(getattr(liasse, "L5_pv_lt_imputees_deficits", 0)),
                d(getattr(liasse, "WS_pv_ct_imposition_differee", 0)),
                d(getattr(liasse, "WT_pv_regime_fusions", 0)),
                d(getattr(liasse, "WU_ecarts_opcvm_deduction", 0)),
                d(getattr(liasse, "WV_regime_mere_filiale", 0)),
                d(getattr(liasse, "L6_produit_net_qp_frais", 0)),
                d(getattr(liasse, "L8_qp_5pct_pv_taux_zero", 0)),
                d(getattr(liasse, "WW_zones_entreprises_exonerees", 0)),
                d(getattr(liasse, "XB_deductions_diverses", 0)),
                d(getattr(liasse, "WZ_majoration_amortissement", 0)),
                d(getattr(liasse, "XA_investissements_outremer", 0)),
            ),
            Decimal("0"),
        )

        rf_brut = rc + reintegrations - deductions
        zi_rf_avant_regimes = rf_brut - sum_abattements(liasse)

        z_l = d(getattr(liasse, "ZL_deficit_reporte_arriere", 0))
        x_i = d(getattr(liasse, "XI_deficits_anterieurs_imputes", 0))
        rf_apres_reports = zi_rf_avant_regimes - z_l - x_i

        xn_benefice = rf_apres_reports if rf_apres_reports > 0 else Decimal("0")
        xo_deficit = abs(rf_apres_reports) if rf_apres_reports < 0 else Decimal("0")
        rf_net = xn_benefice

        return ResultatFiscal(
            rc=money(rc),
            reintegrations=money(reintegrations),
            deductions=money(deductions),
            rf_brut=money(rf_brut),
            rf_net=money(rf_net),
            xr_total_i=money(rc + reintegrations),
            zy_total_ii=money(deductions),
            zi_rf_avant_regimes=money(zi_rf_avant_regimes),
            xn_benefice=money(xn_benefice),
            xo_deficit=money(xo_deficit),
        )

    def calculer_is(self, rf: Decimal, ca_ht: Decimal, capital_75pct_pp: bool) -> CalculIS:
        """Art. 219 CGI: calcul IS avec taux réduit PME si éligible."""
        rf = d(rf)
        ca_ht = d(ca_ht)
        if rf <= 0:
            return CalculIS(
                rf=money(rf),
                pme_eligible=False,
                regime="Déficit ou résultat nul - IS non dû",
                tranche_15pct=Decimal("0"),
                tranche_25pct=Decimal("0"),
                is_total=Decimal("0"),
                acompte_trimestriel=Decimal("0"),
            )

        pme_eligible = ca_ht < self.PLAFOND_CA_PME and capital_75pct_pp

        if pme_eligible:
            t1 = min(rf, self.SEUIL_TAUX_REDUIT)
            t2 = max(rf - self.SEUIL_TAUX_REDUIT, Decimal("0"))
            is_total = t1 * self.TAUX_REDUIT_PME + t2 * self.TAUX_NORMAL
            regime = "PME - Taux réduit Art. 219-I-b CGI"
        else:
            t1 = Decimal("0")
            t2 = rf
            is_total = rf * self.TAUX_NORMAL
            regime = "Taux normal 25% - Art. 219 CGI"

        is_total = money(is_total)
        acompte = money(is_total / Decimal("4"))
        return CalculIS(
            rf=money(rf),
            pme_eligible=pme_eligible,
            regime=regime,
            tranche_15pct=money(t1),
            tranche_25pct=money(t2),
            is_total=is_total,
            acompte_trimestriel=acompte,
        )

    def verifier_mere_filiale(self, p: dict[str, Any]) -> dict[str, Any]:
        """Vérification des 6 conditions cumulatives de l'Art. 145 CGI."""
        conds = {
            "c1_seuil_5pct": d(p.get("pct_capital", 0)) >= Decimal("5"),
            "c2_detention_2ans": d(p.get("annees_detention", 0)) >= Decimal("2"),
            "c3_nominatifs": bool(p.get("nominatifs", False)),
            "c4_pleine_propriete": bool(p.get("pleine_propriete", False)),
            "c5_filiale_IS": bool(p.get("filiale_IS", False)),
            "c6_hors_paradis": not bool(p.get("paradis_fiscal", False)),
        }
        eligible = all(conds.values())

        if eligible:
            div = d(p.get("dividende", 0))
            ci = d(p.get("credit_impot", 0))
            qp = (div + ci) * Decimal("0.05")
            return {
                "eligible": True,
                "deduction_WV": float(money(div)),
                "reintegration_WN_qp5pct": float(money(qp)),
                "impact_rf_net": float(money(-div + qp)),
                "base_legale": "Art. 145 et 216 CGI",
                "conditions": conds,
            }

        return {
            "eligible": False,
            "conds_echec": [k for k, v in conds.items() if not v],
            "consequence": "Dividendes intégralement imposables au taux IS applicable",
            "alerte": "Regime mere-filiale inapplicable",
            "conditions": conds,
        }

