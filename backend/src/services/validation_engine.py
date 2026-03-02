"""
Moteur de validation CGI — Règles fiscales pour le formulaire 2058-A
"""

from typing import List

from src.database.models import Form2058A
from src.schemas.forms import ValidationMessage
from src.services.fiscal_engine import REINTEGRATION_FIELDS, DEDUCTION_FIELDS


# Plafond amortissement véhicule de tourisme (art. 39-4 CGI)
PLAFOND_VEHICULE_STANDARD = 18_300.0
PLAFOND_VEHICULE_POLLUANT = 9_900.0

# Taux max intérêts comptes courants associés (art. 212 bis CGI, 2024)
TAUX_MAX_INTERETS = 5.57


def validate_2058a(form: Form2058A) -> List[ValidationMessage]:
    """Valide le formulaire 2058-A selon les règles du CGI."""
    messages: List[ValidationMessage] = []

    # --- Vérification des valeurs négatives sur les réintégrations ---
    for field in REINTEGRATION_FIELDS:
        value = getattr(form, field) or 0.0
        if value < 0:
            code = field[:2].upper()
            messages.append(ValidationMessage(
                ligne=code,
                niveau="erreur",
                message=f"La ligne {code} ne peut pas être négative ({value:.2f} €)",
            ))

    # --- Vérification des valeurs négatives sur les déductions ---
    for field in DEDUCTION_FIELDS:
        value = getattr(form, field) or 0.0
        if value < 0:
            code = field[:2].upper()
            messages.append(ValidationMessage(
                ligne=code,
                niveau="erreur",
                message=f"La ligne {code} ne peut pas être négative ({value:.2f} €)",
            ))

    # --- Art. 39-4 : Amortissements excédentaires véhicules ---
    we = form.we_amortissements_excessifs or 0.0
    if we > 0:
        messages.append(ValidationMessage(
            ligne="WE",
            niveau="info",
            message=(
                f"Amortissements excédentaires de {we:.2f} €. "
                f"Rappel : plafond véhicule de tourisme = {PLAFOND_VEHICULE_STANDARD:.0f} € "
                f"(ou {PLAFOND_VEHICULE_POLLUANT:.0f} € si CO₂ > 200 g/km)."
            ),
            article_cgi="Art. 39-4 CGI",
        ))

    # --- Art. 212 bis : Intérêts excédentaires ---
    wj = form.wj_interets_excessifs or 0.0
    if wj > 0:
        messages.append(ValidationMessage(
            ligne="WJ",
            niveau="info",
            message=(
                f"Intérêts excédentaires de {wj:.2f} €. "
                f"Taux max déductible : {TAUX_MAX_INTERETS}% (2024)."
            ),
            article_cgi="Art. 212 bis CGI",
        ))

    # --- Amendes et pénalités (toujours non déductibles) ---
    wh = form.wh_amendes_penalites or 0.0
    if wh > 0:
        messages.append(ValidationMessage(
            ligne="WH",
            niveau="info",
            message=(
                f"Amendes et pénalités de {wh:.2f} €. "
                "Rappel : toutes amendes (fiscales, pénales, routières) sont non déductibles."
            ),
            article_cgi="Art. 39-2 CGI",
        ))

    # --- Charges somptuaires ---
    wi = form.wi_charges_somptuaires or 0.0
    if wi > 0:
        messages.append(ValidationMessage(
            ligne="WI",
            niveau="avertissement",
            message=(
                f"Dépenses somptuaires de {wi:.2f} €. "
                "Vérifiez que toutes les dépenses de luxe (bateaux, chasse, résidences) "
                "sont bien réintégrées."
            ),
            article_cgi="Art. 39-4 CGI",
        ))

    # --- Cohérence des totaux ---
    expected_ws = sum(getattr(form, f) or 0.0 for f in REINTEGRATION_FIELDS)
    actual_ws = form.ws_total_reintegrations or 0.0
    if abs(actual_ws - expected_ws) > 0.01:
        messages.append(ValidationMessage(
            ligne="WS",
            niveau="erreur",
            message=(
                f"Total réintégrations incohérent : affiché {actual_ws:.2f} €, "
                f"calculé {expected_ws:.2f} €. Recalculez le formulaire."
            ),
        ))

    expected_wt = sum(getattr(form, f) or 0.0 for f in DEDUCTION_FIELDS)
    actual_wt = form.wt_total_deductions or 0.0
    if abs(actual_wt - expected_wt) > 0.01:
        messages.append(ValidationMessage(
            ligne="WT",
            niveau="erreur",
            message=(
                f"Total déductions incohérent : affiché {actual_wt:.2f} €, "
                f"calculé {expected_wt:.2f} €. Recalculez le formulaire."
            ),
        ))

    # Cohérence résultat fiscal
    wa = form.wa_resultat_comptable or 0.0
    expected_wu = wa + expected_ws - expected_wt
    actual_wu = form.wu_resultat_fiscal or 0.0
    if abs(actual_wu - expected_wu) > 0.01:
        messages.append(ValidationMessage(
            ligne="WU",
            niveau="erreur",
            message=(
                f"Résultat fiscal incohérent : affiché {actual_wu:.2f} €, "
                f"calculé {expected_wu:.2f} €. Recalculez le formulaire."
            ),
        ))

    return messages
