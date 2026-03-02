from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


# --------------------------------------------------------------------------- #
#  2058-A
# --------------------------------------------------------------------------- #
class Form2058AData(BaseModel):
    # Ligne de départ
    wa_resultat_comptable: float = 0.0
    # Réintégrations
    wb_remuneration_exploitant: float = 0.0
    wc_part_deductible: float = 0.0
    wd_avantages_personnels: float = 0.0
    we_amortissements_excessifs: float = 0.0
    wf_impot_societes: float = 0.0
    wg_provisions_non_deductibles: float = 0.0
    wh_amendes_penalites: float = 0.0
    wi_charges_somptuaires: float = 0.0
    wj_interets_excessifs: float = 0.0
    wk_charges_payer_non_deduct: float = 0.0
    wl_autres_reintegrations: float = 0.0
    # Déductions
    wm_quote_part_gie: float = 0.0
    wn_produits_participation: float = 0.0
    wo_plus_values_lt: float = 0.0
    wp_loyers_excessifs: float = 0.0
    wq_reprises_provisions: float = 0.0
    wr_autres_deductions: float = 0.0
    # Notes
    notes: str = ""


class Form2058AResponse(Form2058AData):
    id: int
    exercice_id: int
    ws_total_reintegrations: float
    wt_total_deductions: float
    wu_resultat_fiscal: float
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CalculationResult(BaseModel):
    ws_total_reintegrations: float
    wt_total_deductions: float
    wu_resultat_fiscal: float
    is_benefice: bool


class ValidationMessage(BaseModel):
    ligne: str
    niveau: str  # "erreur", "avertissement", "info"
    message: str
    article_cgi: Optional[str] = None


class ValidationResult(BaseModel):
    valide: bool
    messages: List[ValidationMessage]


# --------------------------------------------------------------------------- #
#  2058-B
# --------------------------------------------------------------------------- #
class Form2058BItemCreate(BaseModel):
    nature: str
    montant: float
    article_cgi: Optional[str] = None
    commentaire: str = ""


class Form2058BItemResponse(BaseModel):
    id: int
    nature: str
    montant: float
    article_cgi: Optional[str]
    commentaire: str

    model_config = {"from_attributes": True}


class Form2058BResponse(BaseModel):
    id: int
    exercice_id: int
    items: List[Form2058BItemResponse]
    total: float
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# --------------------------------------------------------------------------- #
#  2058-C
# --------------------------------------------------------------------------- #
class Form2058CData(BaseModel):
    resultat_exercice: float = 0.0
    report_a_nouveau_anterieur: float = 0.0
    dividendes_distribues: float = 0.0
    reserves_legales: float = 0.0
    reserves_statutaires: float = 0.0
    autres_reserves: float = 0.0
    report_a_nouveau_nouveau: float = 0.0


class Form2058CResponse(Form2058CData):
    id: int
    exercice_id: int
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
