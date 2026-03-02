"""Tests unitaires pour le moteur de calcul fiscal."""

from src.database.models import Form2058A
from src.services.fiscal_engine import calculate_2058a, calculate_is


def _make_form(**kwargs) -> Form2058A:
    form = Form2058A()
    for field in [
        "wa_resultat_comptable",
        "wb_remuneration_exploitant", "wc_part_deductible", "wd_avantages_personnels",
        "we_amortissements_excessifs", "wf_impot_societes", "wg_provisions_non_deductibles",
        "wh_amendes_penalites", "wi_charges_somptuaires", "wj_interets_excessifs",
        "wk_charges_payer_non_deduct", "wl_autres_reintegrations",
        "wm_quote_part_gie", "wn_produits_participation", "wo_plus_values_lt",
        "wp_loyers_excessifs", "wq_reprises_provisions", "wr_autres_deductions",
        "ws_total_reintegrations", "wt_total_deductions", "wu_resultat_fiscal",
    ]:
        setattr(form, field, kwargs.get(field, 0.0))
    return form


class TestCalculate2058A:
    def test_zero_form(self):
        form = _make_form()
        result = calculate_2058a(form)
        assert result["ws_total_reintegrations"] == 0.0
        assert result["wt_total_deductions"] == 0.0
        assert result["wu_resultat_fiscal"] == 0.0
        assert result["is_benefice"] is True

    def test_benefice_simple(self):
        form = _make_form(wa_resultat_comptable=100_000, wh_amendes_penalites=5_000)
        result = calculate_2058a(form)
        assert result["ws_total_reintegrations"] == 5_000.0
        assert result["wt_total_deductions"] == 0.0
        assert result["wu_resultat_fiscal"] == 105_000.0
        assert result["is_benefice"] is True

    def test_deficit(self):
        form = _make_form(
            wa_resultat_comptable=-50_000,
            wh_amendes_penalites=2_000,
            wq_reprises_provisions=10_000,
        )
        result = calculate_2058a(form)
        assert result["ws_total_reintegrations"] == 2_000.0
        assert result["wt_total_deductions"] == 10_000.0
        assert result["wu_resultat_fiscal"] == -58_000.0
        assert result["is_benefice"] is False

    def test_multiple_reintegrations(self):
        form = _make_form(
            wa_resultat_comptable=200_000,
            wb_remuneration_exploitant=30_000,
            we_amortissements_excessifs=5_000,
            wh_amendes_penalites=1_500,
            wj_interets_excessifs=3_000,
        )
        result = calculate_2058a(form)
        assert result["ws_total_reintegrations"] == 39_500.0
        assert result["wu_resultat_fiscal"] == 239_500.0

    def test_reintegrations_and_deductions(self):
        form = _make_form(
            wa_resultat_comptable=150_000,
            wh_amendes_penalites=10_000,
            wg_provisions_non_deductibles=5_000,
            wn_produits_participation=20_000,
            wq_reprises_provisions=3_000,
        )
        result = calculate_2058a(form)
        assert result["ws_total_reintegrations"] == 15_000.0
        assert result["wt_total_deductions"] == 23_000.0
        assert result["wu_resultat_fiscal"] == 142_000.0


class TestCalculateIS:
    def test_deficit(self):
        result = calculate_is(-10_000)
        assert result["is_du"] == 0.0

    def test_pme_low(self):
        result = calculate_is(30_000, is_pme=True)
        assert result["is_du"] == 4_500.0  # 30000 * 15%

    def test_pme_high(self):
        result = calculate_is(100_000, is_pme=True)
        # 42500 * 0.15 + 57500 * 0.25 = 6375 + 14375 = 20750
        assert result["is_du"] == 20_750.0

    def test_normal_rate(self):
        result = calculate_is(100_000, is_pme=False)
        assert result["is_du"] == 25_000.0
