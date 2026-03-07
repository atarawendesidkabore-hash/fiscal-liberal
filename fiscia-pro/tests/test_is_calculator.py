from __future__ import annotations

from decimal import Decimal

from fiscia.is_calculator import ISCalculator
from fiscia.models import Liasse2058AInput


def test_is_calculation_with_canonical_field_names() -> None:
    """Canonical keys must produce expected RF and IS."""
    liasse = Liasse2058AInput(
        siren="123456789",
        exercice_clos="2024-12-31",
        benefice_comptable=Decimal("120000"),
        perte_comptable=Decimal("0"),
        wi_is_comptabilise=Decimal("10000"),
        wg_amendes_penalites=Decimal("2000"),
        wm_interets_excedentaires=Decimal("8000"),
        wn_reintegrations_diverses=Decimal("0"),
        wv_regime_mere_filiale=Decimal("30000"),
        l8_qp_12pct=Decimal("5000"),
    )
    result = ISCalculator.process_liasse(liasse, ca_ht=Decimal("6500000"), capital_75pct_pp=True)

    assert result.rf_brut == Decimal("105000.00")
    assert result.is_total == Decimal("22000.00")


def test_is_calculation_with_legacy_field_names() -> None:
    """Legacy keys must map to the same internal fields and results."""
    liasse = Liasse2058AInput(
        siren="123456789",
        exercice_clos="2024-12-31",
        benefice_comptable=Decimal("120000"),
        perte_comptable=Decimal("0"),
        wi_is_commodite=Decimal("10000"),
        wg_amendes_penalites=Decimal("2000"),
        wm_interets_excedentaires=Decimal("8000"),
        wn_gain_change_qp5=Decimal("0"),
        wv_regime_mere_filiale=Decimal("30000"),
        l8_qp_12pct=Decimal("5000"),
    )
    result = ISCalculator.process_liasse(liasse, ca_ht=Decimal("6500000"), capital_75pct_pp=True)

    assert result.rf_brut == Decimal("105000.00")
    assert result.is_total == Decimal("22000.00")


def test_non_pme_normal_rate() -> None:
    """A non-PME should be taxed at the normal 25% rate."""
    is_total, regime, t15, t25 = ISCalculator.calcul_is(
        rf=Decimal("70000"),
        ca_ht=Decimal("12000000"),
        capital_75pct_pp=True,
    )
    assert is_total == Decimal("17500.00")
    assert t15 == Decimal("0.00")
    assert t25 == Decimal("70000.00")
    assert "Normal" in regime

