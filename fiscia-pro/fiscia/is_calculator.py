from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from .models import ISResult, Liasse2058AInput


class ISCalculator:
    TAUX_NORMAL = Decimal("0.25")
    TAUX_REDUIT_PME = Decimal("0.15")
    SEUIL_REDUIT = Decimal("42500")
    PLAFOND_CA_PME = Decimal("10000000")

    @staticmethod
    def _q(value: Decimal) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def _reintegrations(cls, liasse: Liasse2058AInput) -> Decimal:
        return cls._q(
            liasse.wi_is_comptabilise
            + liasse.wg_amendes_penalites
            + liasse.wm_interets_excedentaires
            + liasse.wn_reintegrations_diverses
        )

    @classmethod
    def _deductions(cls, liasse: Liasse2058AInput) -> Decimal:
        return cls._q(liasse.wv_regime_mere_filiale + liasse.l8_qp_12pct)

    @classmethod
    def _rf_brut_et_net(cls, liasse: Liasse2058AInput) -> tuple[Decimal, Decimal]:
        rf_brut = (
            liasse.benefice_comptable
            - liasse.perte_comptable
            + cls._reintegrations(liasse)
            - cls._deductions(liasse)
        )
        rf_net = rf_brut if rf_brut > 0 else Decimal("0")
        return cls._q(rf_brut), cls._q(rf_net)

    @classmethod
    def calcul_is(
        cls, rf: Decimal | float | int, ca_ht: Decimal | float | int, capital_75pct_pp: bool
    ) -> tuple[Decimal, str, Decimal, Decimal]:
        rf = Decimal(str(rf))
        ca_ht = Decimal(str(ca_ht))

        if rf <= 0:
            return Decimal("0.00"), "Resultat nul ou deficit", Decimal("0.00"), Decimal("0.00")

        pme_eligible = ca_ht < cls.PLAFOND_CA_PME and capital_75pct_pp
        if pme_eligible:
            tranche_15 = min(rf, cls.SEUIL_REDUIT)
            tranche_25 = max(rf - cls.SEUIL_REDUIT, Decimal("0"))
            is_total = tranche_15 * cls.TAUX_REDUIT_PME + tranche_25 * cls.TAUX_NORMAL
            regime = "PME - Art. 219-I-b CGI (LFI 2024)"
        else:
            tranche_15 = Decimal("0")
            tranche_25 = rf
            is_total = rf * cls.TAUX_NORMAL
            regime = "Normal - Art. 219 CGI (LFI 2024)"

        return cls._q(is_total), regime, cls._q(tranche_15), cls._q(tranche_25)

    @classmethod
    def process_liasse(
        cls, liasse: Liasse2058AInput, ca_ht: Decimal | float | int, capital_75pct_pp: bool
    ) -> ISResult:
        rf_brut, rf_net = cls._rf_brut_et_net(liasse)
        is_total, regime, t15, t25 = cls.calcul_is(rf_net, ca_ht, capital_75pct_pp)
        acompte = cls._q(is_total / Decimal("4")) if is_total > 0 else Decimal("0.00")
        return ISResult(
            rf_brut=rf_brut,
            rf_net=rf_net,
            is_total=is_total,
            regime=regime,
            acompte_trimestriel=acompte,
            details={
                "reintegrations": cls._reintegrations(liasse),
                "deductions": cls._deductions(liasse),
                "tranche_15": t15,
                "tranche_25": t25,
            },
        )

