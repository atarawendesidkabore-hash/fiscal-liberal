from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class _FlexibleBaseModel(BaseModel):
    # Pydantic v2 canonical option equivalent to allow_population_by_field_name.
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class Liasse2058AInput(_FlexibleBaseModel):
    siren: str = Field(..., min_length=9, max_length=9, description="SIREN (9 chiffres)")
    exercice_clos: date = Field(..., description="Date de cloture (YYYY-MM-DD)")

    benefice_comptable: Decimal = Field(..., description="Benefice comptable (WA)")
    perte_comptable: Decimal = Field(..., description="Perte comptable (WQ)")

    wi_is_comptabilise: Decimal = Field(Decimal("0"), alias="wi_is_commodite")
    wg_amendes_penalites: Decimal = Field(Decimal("0"))
    wm_interets_excedentaires: Decimal = Field(Decimal("0"))
    wn_reintegrations_diverses: Decimal = Field(Decimal("0"), alias="wn_gain_change_qp5")

    wv_regime_mere_filiale: Decimal = Field(Decimal("0"))
    l8_qp_12pct: Decimal = Field(Decimal("0"))


class MereFilialeInput(_FlexibleBaseModel):
    pct_capital: Decimal = Field(Decimal("0"))
    annees_detention: Decimal = Field(Decimal("0"))
    nominatifs: bool = Field(False, alias="nominatif")
    pleine_propriete: bool = Field(False)
    filiale_is: bool = Field(False)
    paradis_fiscal: bool = Field(False)
    dividende: Decimal = Field(Decimal("0"), alias="dividende_brut")
    credit_impot: Decimal = Field(Decimal("0"))


class ISResult(_FlexibleBaseModel):
    rf_brut: Decimal
    rf_net: Decimal
    is_total: Decimal
    regime: str
    acompte_trimestriel: Decimal
    details: dict
