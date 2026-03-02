from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ExerciceCreate(BaseModel):
    company_id: int
    date_debut: date
    date_fin: date
    cloture: Optional[date] = None


class ExerciceUpdate(BaseModel):
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    cloture: Optional[date] = None
    statut: Optional[str] = None  # brouillon, valide, depose


class ExerciceResponse(BaseModel):
    id: int
    company_id: int
    date_debut: date
    date_fin: date
    cloture: Optional[date]
    statut: str
    created_at: datetime

    model_config = {"from_attributes": True}
