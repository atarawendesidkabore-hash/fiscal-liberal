from __future__ import annotations

from decimal import Decimal

from fiscia.mere_fi_check import verifier_mere_filiale


def test_mere_filiale_with_canonical_names() -> None:
    """Canonical naming should validate eligibility and compute WV/WN correctly."""
    result = verifier_mere_filiale(
        {
            "pct_capital": Decimal("7"),
            "annees_detention": Decimal("3"),
            "nominatifs": True,
            "pleine_propriete": True,
            "filiale_is": True,
            "paradis_fiscal": False,
            "dividende": Decimal("50000"),
            "credit_impot": Decimal("0"),
        }
    )
    assert result["eligible"] is True
    assert result["deduction_WV"] == Decimal("50000.00")
    assert result["reintegration_WN_qp5"] == Decimal("2500.00")


def test_mere_filiale_with_legacy_names() -> None:
    """Legacy naming must keep backward compatibility for existing clients."""
    result = verifier_mere_filiale(
        {
            "pct_capital": Decimal("7"),
            "annees_detention": Decimal("3"),
            "nominatif": True,
            "pleine_propriete": True,
            "filiale_is": True,
            "paradis_fiscal": False,
            "dividende_brut": Decimal("50000"),
            "credit_impot": Decimal("0"),
        }
    )
    assert result["eligible"] is True
    assert result["deduction_WV"] == Decimal("50000.00")
    assert result["reintegration_WN_qp5"] == Decimal("2500.00")


def test_mere_filiale_missing_condition() -> None:
    """If one Art. 145 condition fails, eligibility must be False with explicit code."""
    result = verifier_mere_filiale(
        {
            "pct_capital": Decimal("7"),
            "annees_detention": Decimal("1"),
            "nominatifs": True,
            "pleine_propriete": True,
            "filiale_is": True,
            "paradis_fiscal": False,
            "dividende": Decimal("50000"),
            "credit_impot": Decimal("0"),
        }
    )
    assert result["eligible"] is False
    assert "c2_detention_2ans" in result["failed_conditions"]

