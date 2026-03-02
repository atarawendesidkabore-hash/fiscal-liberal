from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User, Exercice, Company, Form2058C
from src.schemas.forms import Form2058CData, Form2058CResponse
from src.utils.security import get_current_user

router = APIRouter()


def _get_form_c(exercice_id: int, user: User, db: Session) -> Form2058C:
    exercice = db.query(Exercice).filter(Exercice.id == exercice_id).first()
    if not exercice:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    company = db.query(Company).filter(
        Company.id == exercice.company_id, Company.user_id == user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Société introuvable")
    form = db.query(Form2058C).filter(Form2058C.exercice_id == exercice_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulaire 2058-C introuvable")
    return form


@router.get("/{exercice_id}/2058c", response_model=Form2058CResponse)
def get_2058c(
    exercice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_form_c(exercice_id, current_user, db)


@router.put("/{exercice_id}/2058c", response_model=Form2058CResponse)
def save_2058c(
    exercice_id: int,
    data: Form2058CData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = _get_form_c(exercice_id, current_user, db)
    for field, value in data.model_dump().items():
        setattr(form, field, value)
    db.commit()
    db.refresh(form)
    return form
