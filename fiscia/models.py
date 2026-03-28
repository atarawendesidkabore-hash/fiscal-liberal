from decimal import Decimal
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class Liasse2058AInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    siren: str = Field(..., min_length=9, max_length=9, description="SIREN de l'entreprise")
    exercice_clos: str = Field(..., description="Date de cloture au format YYYY-MM-DD")
    benefice_comptable: Decimal = Field(default=Decimal("0"), description="WA - Benefice comptable")
    perte_comptable: Decimal = Field(default=Decimal("0"), description="WQ - Perte comptable")
    wi_is_comptabilise: Decimal = Field(default=Decimal("0"), alias="wi_is_commodite", description="WI - IS comptabilise en charges (Art. 213 CGI)")
    wg_amendes_penalites: Decimal = Field(default=Decimal("0"), description="WG - Amendes et penalites (Art. 39-2 CGI)")
    wm_interets_excedentaires: Decimal = Field(default=Decimal("0"), description="WM - Interets excedentaires CC associes (Art. 39-1-3 + 212 CGI)")
    wn_reintegrations_diverses: Decimal = Field(default=Decimal("0"), alias="wn_gain_change_qp5", description="WN - Reintegrations diverses dont QP 5% mere-filiale")
    wv_regime_mere_filiale: Decimal = Field(default=Decimal("0"), description="WV - Deduction regime mere-filiale (Art. 145 + 216 CGI)")
    l8_qp_12pct: Decimal = Field(default=Decimal("0"), description="L8 - QP 12% PV LT titres participation (Art. 219-I-a quater CGI)")


class ISResult(BaseModel):
    rf_brut: Decimal = Field(..., description="Resultat fiscal brut avant deficits")
    rf_net: Decimal = Field(..., description="Resultat fiscal net (base IS)")
    is_total: Decimal = Field(..., description="IS total du")
    regime: str = Field(..., description="Regime applicable (PME taux reduit / Normal)")
    acompte_trimestriel: Decimal = Field(..., description="Acompte trimestriel IS (IS / 4)")
    details: Dict[str, Decimal] = Field(default_factory=dict, description="Detail du calcul")
    disclaimer: str = Field(
        default="Reponse indicative. Toute decision fiscale engageante necessite l'analyse personnalisee d'un professionnel qualifie.",
        description="Disclaimer obligatoire",
    )


class Liasse2058BCInput(BaseModel):
    deficits_reportables_ouverture: Decimal = Field(
        default=Decimal("0"),
        description="Deficits fiscaux reportables a l'ouverture de l'exercice",
    )
    moins_values_lt_ouverture: Decimal = Field(
        default=Decimal("0"),
        description="Moins-values long terme reportables a l'ouverture",
    )
    moins_values_lt_imputees: Decimal = Field(
        default=Decimal("0"),
        description="Moins-values long terme imputees sur l'exercice",
    )
    acomptes_verses: Decimal = Field(
        default=Decimal("0"),
        description="Acomptes d'IS deja verses",
    )
    credits_impot: Decimal = Field(
        default=Decimal("0"),
        description="Credits d'impot imputables",
    )
    contribution_sociale: Decimal = Field(
        default=Decimal("0"),
        description="Contribution additionnelle ou sociale a ajouter au solde",
    )
    regularisations: Decimal = Field(
        default=Decimal("0"),
        description="Regularisations manuelles ou autres supplements",
    )


class Liasse2058BCResult(BaseModel):
    tableau_2058b: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Brouillon de travail 2058-B",
    )
    tableau_2058c: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Brouillon de travail 2058-C",
    )
    regime: str = Field(..., description="Regime IS retenu apres reports")
    notes: List[str] = Field(
        default_factory=list,
        description="Commentaires de preparation et points d'attention",
    )
    disclaimer: str = Field(
        default="Reponse indicative. Toute decision fiscale engageante necessite l'analyse personnalisee d'un professionnel qualifie.",
        description="Disclaimer obligatoire",
    )
