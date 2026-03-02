from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    raison_sociale: str
    forme_juridique: str  # SELARL, SELAS, SAS, SARL, EI, EURL
    siren: Optional[str] = None
    siret: Optional[str] = None
    code_ape: Optional[str] = None
    adresse: Optional[str] = None
    capital_social: float = 0.0
    date_creation: Optional[date] = None


class CompanyUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    forme_juridique: Optional[str] = None
    siren: Optional[str] = None
    siret: Optional[str] = None
    code_ape: Optional[str] = None
    adresse: Optional[str] = None
    capital_social: Optional[float] = None
    date_creation: Optional[date] = None


class CompanyResponse(BaseModel):
    id: int
    raison_sociale: str
    forme_juridique: str
    siren: Optional[str]
    siret: Optional[str]
    code_ape: Optional[str]
    adresse: Optional[str]
    capital_social: float
    date_creation: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}
