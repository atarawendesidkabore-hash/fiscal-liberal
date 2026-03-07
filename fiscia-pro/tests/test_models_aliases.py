from __future__ import annotations

from datetime import date
from decimal import Decimal

from fiscia.models import Liasse2058AInput, MereFilialeInput


def test_liasse_accepts_legacy_and_canonical_fields() -> None:
    liasse = Liasse2058AInput(
        siren="123456789",
        exercice_clos=date(2024, 12, 31),
        benefice_comptable=Decimal("100000"),
        perte_comptable=Decimal("0"),
        wi_is_commodite=Decimal("1000"),
        wn_gain_change_qp5=Decimal("500"),
        wg_amendes_penalites=Decimal("0"),
        wm_interets_excedentaires=Decimal("0"),
        wv_regime_mere_filiale=Decimal("0"),
        l8_qp_12pct=Decimal("0"),
    )

    assert liasse.wi_is_comptabilise == Decimal("1000")
    assert liasse.wn_reintegrations_diverses == Decimal("500")

    liasse2 = Liasse2058AInput(
        siren="123456789",
        exercice_clos=date(2024, 12, 31),
        benefice_comptable=Decimal("100000"),
        perte_comptable=Decimal("0"),
        wi_is_comptabilise=Decimal("700"),
        wn_reintegrations_diverses=Decimal("300"),
        wg_amendes_penalites=Decimal("0"),
        wm_interets_excedentaires=Decimal("0"),
        wv_regime_mere_filiale=Decimal("0"),
        l8_qp_12pct=Decimal("0"),
    )
    assert liasse2.wi_is_comptabilise == Decimal("700")
    assert liasse2.wn_reintegrations_diverses == Decimal("300")


def test_mere_filiale_aliases() -> None:
    m = MereFilialeInput(
        pct_capital=Decimal("7"),
        annees_detention=Decimal("3"),
        nominatif=True,
        pleine_propriete=True,
        filiale_is=True,
        paradis_fiscal=False,
        dividende_brut=Decimal("50000"),
        credit_impot=Decimal("0"),
    )
    assert m.nominatifs is True
    assert m.dividende == Decimal("50000")

