"""Tests du verificateur mere-filiale Art. 145 CGI."""
from fiscia.mere_fi_check import verifier_mere_filiale


def test_all_conditions_met():
    """6 conditions remplies -> eligible, QP 5% correcte."""
    params = {
        "pct_capital": 7,
        "annees_detention": 3,
        "nominatifs": True,
        "pleine_propriete": True,
        "filiale_is": True,
        "paradis_fiscal": False,
        "dividende": 50000,
        "credit_impot": 0,
    }
    result = verifier_mere_filiale(params)

    assert result["eligible"] is True
    assert result["deduction_WV"] == 50000.0
    # QP 5% = (50000 + 0) * 5% = 2500
    assert result["reintegration_WN_qp5"] == 2500.0
    # Impact = -50000 + 2500 = -47500
    assert result["impact_rf_net"] == -47500.0
    assert result["base_legale"] == "Art. 145 et 216 CGI"


def test_one_condition_missing():
    """detention < 2 ans -> non eligible."""
    params = {
        "pct_capital": 10,
        "annees_detention": 1,
        "nominatifs": True,
        "pleine_propriete": True,
        "filiale_is": True,
        "paradis_fiscal": False,
        "dividende": 100000,
        "credit_impot": 5000,
    }
    result = verifier_mere_filiale(params)

    assert result["eligible"] is False
    assert "c2_detention_2ans" in result["conditions_echouees"]
    assert "INAPPLICABLE" in result["alerte"]


def test_paradis_fiscal_blocks():
    """Filiale dans un ETNC -> condition 6 echouee."""
    params = {
        "pct_capital": 20,
        "annees_detention": 5,
        "nominatifs": True,
        "pleine_propriete": True,
        "filiale_is": True,
        "paradis_fiscal": True,
        "dividende": 80000,
        "credit_impot": 0,
    }
    result = verifier_mere_filiale(params)

    assert result["eligible"] is False
    assert "c6_hors_paradis" in result["conditions_echouees"]


def test_qp5_with_credit_impot():
    """QP 5% se calcule sur dividende + credit d'impot."""
    params = {
        "pct_capital": 5,
        "annees_detention": 2,
        "nominatifs": True,
        "pleine_propriete": True,
        "filiale_is": True,
        "paradis_fiscal": False,
        "dividende": 100000,
        "credit_impot": 10000,
    }
    result = verifier_mere_filiale(params)

    assert result["eligible"] is True
    # QP 5% = (100000 + 10000) * 5% = 5500
    assert result["reintegration_WN_qp5"] == 5500.0
