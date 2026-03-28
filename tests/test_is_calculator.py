"""Tests du moteur IS - Art. 219 CGI."""
from decimal import Decimal

from fiscia.is_calculator import ISCalculator
from fiscia.models import Liasse2058AInput


calc = ISCalculator()


def test_pme_reduced_rate():
    """PME: RF=70000, CA=5M, capital>=75% PP -> IS = 42500*15% + 27500*25% = 6375 + 6875 = 13250."""
    is_total, regime, t15, t25 = calc.calcul_is(
        Decimal("70000"), Decimal("5000000"), True
    )
    assert is_total == Decimal("13250.00")
    assert "PME" in regime
    assert t15 == Decimal("42500")
    assert t25 == Decimal("27500")


def test_non_pme_normal_rate():
    """Non-PME: RF=70000, CA=12M -> IS = 70000*25% = 17500."""
    is_total, regime, t15, t25 = calc.calcul_is(
        Decimal("70000"), Decimal("12000000"), True
    )
    assert is_total == Decimal("17500.00")
    assert "normal" in regime.lower()
    assert t15 == Decimal("0")
    assert t25 == Decimal("70000")


def test_full_liasse_pme():
    """
    Liasse complete PME:
    Benefice=120000, WI=10000, WG=2000, WM=8000, WV=30000, L8=5000
    RC = 120000
    Reintegrations = 10000 + 2000 + 8000 + 0 + 5000 = 25000
    Deductions = 30000
    RF brut = 120000 + 25000 - 30000 = 115000
    RF net = 115000
    IS = 42500*15% + 72500*25% = 6375 + 18125 = 24500
    """
    liasse = Liasse2058AInput(
        siren="123456789",
        exercice_clos="2024-12-31",
        benefice_comptable=Decimal("120000"),
        wi_is_comptabilise=Decimal("10000"),
        wg_amendes_penalites=Decimal("2000"),
        wm_interets_excedentaires=Decimal("8000"),
        wv_regime_mere_filiale=Decimal("30000"),
        l8_qp_12pct=Decimal("5000"),
    )
    result = calc.process_liasse(liasse, Decimal("6500000"), True)

    assert result.rf_brut == Decimal("115000")
    assert result.rf_net == Decimal("115000")
    assert result.is_total == Decimal("24500.00")
    assert "PME" in result.regime


def test_deficit_no_is():
    """Si RF negatif, IS = 0."""
    is_total, regime, _, _ = calc.calcul_is(
        Decimal("-50000"), Decimal("5000000"), True
    )
    assert is_total == Decimal("0")
    assert "Deficit" in regime


def test_acompte_calculation():
    """Acompte = IS / 4."""
    liasse = Liasse2058AInput(
        siren="987654321",
        exercice_clos="2024-12-31",
        benefice_comptable=Decimal("100000"),
    )
    result = calc.process_liasse(liasse, Decimal("5000000"), True)
    expected_acompte = (result.is_total / 4).quantize(Decimal("0.01"))
    assert result.acompte_trimestriel == expected_acompte
