"""
Moteur de calcul IS conforme Art. 219 CGI - LFI 2024
PME taux reduit : Art. 219-I-b CGI
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

from fiscia.models import Liasse2058AInput, ISResult

TAUX_NORMAL = Decimal("0.25")
TAUX_REDUIT_PME = Decimal("0.15")
SEUIL_REDUIT = Decimal("42500")
PLAFOND_CA_PME = Decimal("10000000")

DISCLAIMER = (
    "Reponse indicative. Toute decision fiscale engageante "
    "necessite l'analyse personnalisee d'un professionnel qualifie."
)


class ISCalculator:

    def _reintegrations(self, liasse: Liasse2058AInput) -> Decimal:
        return (
            liasse.wi_is_comptabilise
            + liasse.wg_amendes_penalites
            + liasse.wm_interets_excedentaires
            + liasse.wn_reintegrations_diverses
            + liasse.l8_qp_12pct
        )

    def _deductions(self, liasse: Liasse2058AInput) -> Decimal:
        return liasse.wv_regime_mere_filiale

    def _rf_brut_et_net(self, liasse: Liasse2058AInput) -> Tuple[Decimal, Decimal]:
        rc = liasse.benefice_comptable - liasse.perte_comptable
        reint = self._reintegrations(liasse)
        deduc = self._deductions(liasse)
        rf_brut = rc + reint - deduc
        rf_net = max(rf_brut, Decimal("0"))
        return rf_brut, rf_net

    def calcul_is(
        self,
        rf: Decimal,
        ca_ht: Decimal,
        capital_75pct_pp: bool,
    ) -> Tuple[Decimal, str, Decimal, Decimal]:
        """
        Calcule l'IS du selon Art. 219 CGI.
        Returns (is_total, regime, tranche_15, tranche_25).
        """
        rf = Decimal(str(rf))
        ca_ht = Decimal(str(ca_ht))

        if rf <= 0:
            return Decimal("0"), "Deficit - pas d'IS du", Decimal("0"), Decimal("0")

        pme_eligible = ca_ht < PLAFOND_CA_PME and capital_75pct_pp

        if pme_eligible:
            tranche_15 = min(rf, SEUIL_REDUIT)
            tranche_25 = max(rf - SEUIL_REDUIT, Decimal("0"))
            is_total = (
                tranche_15 * TAUX_REDUIT_PME + tranche_25 * TAUX_NORMAL
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            regime = "PME - Taux reduit Art. 219-I-b CGI"
        else:
            tranche_15 = Decimal("0")
            tranche_25 = rf
            is_total = (rf * TAUX_NORMAL).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            regime = "Taux normal 25% - Art. 219 CGI"

        return is_total, regime, tranche_15, tranche_25

    def process_liasse(
        self,
        liasse: Liasse2058AInput,
        ca_ht: Decimal,
        capital_75pct_pp: bool,
    ) -> ISResult:
        """Traite une liasse 2058-A complete et retourne le resultat IS."""
        ca_ht = Decimal(str(ca_ht))
        rf_brut, rf_net = self._rf_brut_et_net(liasse)
        is_total, regime, tranche_15, tranche_25 = self.calcul_is(
            rf_net, ca_ht, capital_75pct_pp
        )
        acompte = (is_total / 4).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return ISResult(
            rf_brut=rf_brut,
            rf_net=rf_net,
            is_total=is_total,
            regime=regime,
            acompte_trimestriel=acompte,
            details={
                "resultat_comptable": liasse.benefice_comptable - liasse.perte_comptable,
                "total_reintegrations": self._reintegrations(liasse),
                "total_deductions": self._deductions(liasse),
                "tranche_15pct": tranche_15,
                "tranche_25pct": tranche_25,
            },
            disclaimer=DISCLAIMER,
        )
