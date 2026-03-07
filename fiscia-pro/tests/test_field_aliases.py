from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from fiscia.guardrails import GuardrailError, MANDATORY_DISCLAIMER, enforce_guardrails
from fiscia.models import Liasse2058AInput, MereFilialeInput


def test_pydantic_accepts_old_and_new_liasse_names() -> None:
    """Both canonical and legacy liasse keys must map to the same internal values."""
    old_payload = {
        "siren": "123456789",
        "exercice_clos": "2024-12-31",
        "benefice_comptable": "120000",
        "perte_comptable": "0",
        "wi_is_commodite": "10000",
        "wn_gain_change_qp5": "5000",
        "wg_amendes_penalites": "0",
        "wm_interets_excedentaires": "0",
        "wv_regime_mere_filiale": "0",
        "l8_qp_12pct": "0",
    }
    new_payload = {
        "siren": "123456789",
        "exercice_clos": "2024-12-31",
        "benefice_comptable": "120000",
        "perte_comptable": "0",
        "wi_is_comptabilise": "10000",
        "wn_reintegrations_diverses": "5000",
        "wg_amendes_penalites": "0",
        "wm_interets_excedentaires": "0",
        "wv_regime_mere_filiale": "0",
        "l8_qp_12pct": "0",
    }

    model_old = Liasse2058AInput(**old_payload)
    model_new = Liasse2058AInput(**new_payload)

    assert model_old.wi_is_comptabilise == model_new.wi_is_comptabilise == Decimal("10000")
    assert model_old.wn_reintegrations_diverses == model_new.wn_reintegrations_diverses == Decimal("5000")


def test_pydantic_accepts_old_and_new_mere_names() -> None:
    """Both canonical and legacy mother-subsidiary keys must parse identically."""
    old_payload = {
        "pct_capital": "7",
        "annees_detention": "3",
        "nominatif": True,
        "pleine_propriete": True,
        "filiale_is": True,
        "paradis_fiscal": False,
        "dividende_brut": "50000",
        "credit_impot": "0",
    }
    new_payload = {
        "pct_capital": "7",
        "annees_detention": "3",
        "nominatifs": True,
        "pleine_propriete": True,
        "filiale_is": True,
        "paradis_fiscal": False,
        "dividende": "50000",
        "credit_impot": "0",
    }

    model_old = MereFilialeInput(**old_payload)
    model_new = MereFilialeInput(**new_payload)

    assert model_old.nominatifs is True and model_new.nominatifs is True
    assert model_old.dividende == model_new.dividende == Decimal("50000")


def test_invalid_field_name_is_rejected() -> None:
    """Malformed unknown fields must fail fast with a validation error."""
    with pytest.raises(ValidationError):
        Liasse2058AInput(
            siren="123456789",
            exercice_clos=date(2024, 12, 31),
            benefice_comptable=Decimal("1"),
            perte_comptable=Decimal("0"),
            wi_is_wrong_name=Decimal("10"),
            wg_amendes_penalites=Decimal("0"),
            wm_interets_excedentaires=Decimal("0"),
            wn_reintegrations_diverses=Decimal("0"),
            wv_regime_mere_filiale=Decimal("0"),
            l8_qp_12pct=Decimal("0"),
        )


def test_guardrails_pass_with_old_or_new_naming_in_response() -> None:
    """Guardrails should behave the same even if response text mentions legacy labels."""
    context = {
        "pme_checked": True,
        "mere_conditions_present": True,
        "confidential": True,
        "module": "liasse",
    }

    old_answer = (
        "WI (wi_is_commodite): 10,000 EUR\n"
        "WN (wn_gain_change_qp5): 5,000 EUR\n"
        "Base legale: Art. 219 CGI (LFI 2024)\n\n"
        f"{MANDATORY_DISCLAIMER}"
    )
    new_answer = (
        "WI (wi_is_comptabilise): 10,000 EUR\n"
        "WN (wn_reintegrations_diverses): 5,000 EUR\n"
        "Base legale: Art. 219 CGI (LFI 2024)\n\n"
        f"{MANDATORY_DISCLAIMER}"
    )

    assert enforce_guardrails(old_answer, context) == old_answer
    assert enforce_guardrails(new_answer, context) == new_answer


def test_guardrails_fail_without_pme_check() -> None:
    """IS amount must be blocked when PME check is missing."""
    answer = f"IS total: 12,000 EUR\nArt. 219 CGI (LFI 2024)\n\n{MANDATORY_DISCLAIMER}"
    with pytest.raises(GuardrailError):
        enforce_guardrails(
            answer,
            {
                "pme_checked": False,
                "mere_conditions_present": True,
                "confidential": True,
                "module": "calc-is",
            },
        )

