from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

from backend.services.is_calculator import ISCalculator
from backend.services.plus_values import PlusValuesService


def make_liasse(**kwargs) -> SimpleNamespace:
    defaults = {
        "WA_benefice_comptable": Decimal("0"),
        "WQ_perte_comptable": Decimal("0"),
        "ZL_deficit_reporte_arriere": Decimal("0"),
        "XI_deficits_anterieurs_imputes": Decimal("0"),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_01_rf_zero() -> None:
    calc = ISCalculator()
    rf = calc.calculer_rf(make_liasse())
    assert rf.rf_net == Decimal("0.00")
    assert rf.xn_benefice == Decimal("0.00")
    assert rf.xo_deficit == Decimal("0.00")


def test_02_rf_reintegrations_wi_wg_wm() -> None:
    calc = ISCalculator()
    rf = calc.calculer_rf(
        make_liasse(
            WA_benefice_comptable=Decimal("100000"),
            WI_is_et_ifa=Decimal("22000"),
            WG_amendes_penalites=Decimal("3500"),
            WM_interets_excedentaires=Decimal("8000"),
        )
    )
    assert rf.reintegrations == Decimal("33500.00")
    assert rf.rf_brut == Decimal("133500.00")


def test_03_rf_mere_filiale_wv_wn() -> None:
    calc = ISCalculator()
    rf = calc.calculer_rf(
        make_liasse(
            WA_benefice_comptable=Decimal("100000"),
            WN_reintegrations_diverses=Decimal("2500"),
            WV_regime_mere_filiale=Decimal("50000"),
        )
    )
    assert rf.rf_brut == Decimal("52500.00")
    assert rf.rf_net == Decimal("52500.00")


def test_04_rf_abattements_section_iii() -> None:
    calc = ISCalculator()
    rf = calc.calculer_rf(
        make_liasse(
            WA_benefice_comptable=Decimal("100000"),
            XD_entreprises_nouvelles_44sexies=Decimal("10000"),
        )
    )
    assert rf.zi_rf_avant_regimes == Decimal("90000.00")
    assert rf.rf_net == Decimal("90000.00")


def test_05_rf_generates_deficit() -> None:
    calc = ISCalculator()
    rf = calc.calculer_rf(
        make_liasse(
            WA_benefice_comptable=Decimal("20000"),
            XI_deficits_anterieurs_imputes=Decimal("30000"),
        )
    )
    assert rf.rf_net == Decimal("0.00")
    assert rf.xo_deficit == Decimal("10000.00")


def test_06_rf_with_plus_values_and_deductions() -> None:
    calc = ISCalculator()
    rf = calc.calculer_rf(
        make_liasse(
            WA_benefice_comptable=Decimal("120000"),
            WR_mv_lt_taux_15_8_0=Decimal("5000"),
            WG_amendes_penalites=Decimal("1000"),
            WI_is_et_ifa=Decimal("12000"),
            XB_deductions_diverses=Decimal("2000"),
        )
    )
    assert rf.reintegrations == Decimal("13000.00")
    assert rf.deductions == Decimal("7000.00")
    assert rf.rf_net == Decimal("126000.00")


def test_07_rf_rounding_to_cent() -> None:
    calc = ISCalculator()
    rf = calc.calculer_rf(
        make_liasse(
            WA_benefice_comptable=Decimal("1000.015"),
            WG_amendes_penalites=Decimal("0.005"),
        )
    )
    assert rf.rf_net == Decimal("1000.02")


def test_08_is_normal_rate() -> None:
    calc = ISCalculator()
    result = calc.calculer_is(Decimal("100000"), Decimal("12000000"), False)
    assert result.pme_eligible is False
    assert result.is_total == Decimal("25000.00")


def test_09_is_pme_below_threshold() -> None:
    calc = ISCalculator()
    result = calc.calculer_is(Decimal("30000"), Decimal("5000000"), True)
    assert result.pme_eligible is True
    assert result.tranche_15pct == Decimal("30000.00")
    assert result.is_total == Decimal("4500.00")


def test_10_is_pme_split_threshold() -> None:
    calc = ISCalculator()
    result = calc.calculer_is(Decimal("100000"), Decimal("5000000"), True)
    assert result.tranche_15pct == Decimal("42500.00")
    assert result.tranche_25pct == Decimal("57500.00")
    assert result.is_total == Decimal("20750.00")


def test_11_is_ca_boundary_not_eligible() -> None:
    calc = ISCalculator()
    result = calc.calculer_is(Decimal("100000"), Decimal("10000000"), True)
    assert result.pme_eligible is False
    assert result.is_total == Decimal("25000.00")


def test_12_is_zero_result() -> None:
    calc = ISCalculator()
    result = calc.calculer_is(Decimal("0"), Decimal("1000000"), True)
    assert result.is_total == Decimal("0")


def test_13_is_negative_result() -> None:
    calc = ISCalculator()
    result = calc.calculer_is(Decimal("-500"), Decimal("1000000"), True)
    assert result.is_total == Decimal("0")


def test_14_mere_filiale_eligible() -> None:
    calc = ISCalculator()
    result = calc.verifier_mere_filiale(
        {
            "pct_capital": 7,
            "annees_detention": 3,
            "nominatifs": True,
            "pleine_propriete": True,
            "filiale_IS": True,
            "paradis_fiscal": False,
            "dividende": 50000,
            "credit_impot": 0,
        }
    )
    assert result["eligible"] is True
    assert result["deduction_WV"] == 50000.0
    assert result["reintegration_WN_qp5pct"] == 2500.0
    assert result["impact_rf_net"] == -47500.0


def test_15_mere_filiale_fail_c1() -> None:
    calc = ISCalculator()
    result = calc.verifier_mere_filiale(
        {
            "pct_capital": 4.9,
            "annees_detention": 3,
            "nominatifs": True,
            "pleine_propriete": True,
            "filiale_IS": True,
            "paradis_fiscal": False,
        }
    )
    assert result["eligible"] is False
    assert "c1_seuil_5pct" in result["conds_echec"]


def test_16_mere_filiale_fail_c2() -> None:
    calc = ISCalculator()
    result = calc.verifier_mere_filiale(
        {
            "pct_capital": 5,
            "annees_detention": 1,
            "nominatifs": True,
            "pleine_propriete": True,
            "filiale_IS": True,
            "paradis_fiscal": False,
        }
    )
    assert result["eligible"] is False
    assert "c2_detention_2ans" in result["conds_echec"]


def test_17_mere_filiale_fail_c3() -> None:
    calc = ISCalculator()
    result = calc.verifier_mere_filiale(
        {
            "pct_capital": 5,
            "annees_detention": 2,
            "nominatifs": False,
            "pleine_propriete": True,
            "filiale_IS": True,
            "paradis_fiscal": False,
        }
    )
    assert result["eligible"] is False
    assert "c3_nominatifs" in result["conds_echec"]


def test_18_mere_filiale_fail_c4() -> None:
    calc = ISCalculator()
    result = calc.verifier_mere_filiale(
        {
            "pct_capital": 5,
            "annees_detention": 2,
            "nominatifs": True,
            "pleine_propriete": False,
            "filiale_IS": True,
            "paradis_fiscal": False,
        }
    )
    assert result["eligible"] is False
    assert "c4_pleine_propriete" in result["conds_echec"]


def test_19_mere_filiale_fail_c5_and_c6() -> None:
    calc = ISCalculator()
    result = calc.verifier_mere_filiale(
        {
            "pct_capital": 5,
            "annees_detention": 2,
            "nominatifs": True,
            "pleine_propriete": True,
            "filiale_IS": False,
            "paradis_fiscal": True,
        }
    )
    assert result["eligible"] is False
    assert "c5_filiale_IS" in result["conds_echec"]
    assert "c6_hors_paradis" in result["conds_echec"]


def test_20_plus_values_qp12pct() -> None:
    service = PlusValuesService()
    result = service.calculer_pv_lt_titres_participation(
        plus_value_brute=Decimal("100000"),
        moins_values_lt_imputables=Decimal("25000"),
    )
    assert result["base_taux_zero"] == 75000.0
    assert result["reintegration_l8_qp12pct"] == 9000.0

