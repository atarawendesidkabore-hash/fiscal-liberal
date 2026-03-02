from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User, Exercice, Company, Form2058A
from src.schemas.forms import Form2058AData, Form2058AResponse, CalculationResult, ValidationResult
from src.services.fiscal_engine import calculate_2058a
from src.services.validation_engine import validate_2058a
from src.utils.security import get_current_user

router = APIRouter()


def _get_form(exercice_id: int, user: User, db: Session) -> Form2058A:
    exercice = db.query(Exercice).filter(Exercice.id == exercice_id).first()
    if not exercice:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    company = db.query(Company).filter(
        Company.id == exercice.company_id, Company.user_id == user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Société introuvable")
    form = db.query(Form2058A).filter(Form2058A.exercice_id == exercice_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulaire 2058-A introuvable")
    return form


@router.get("/{exercice_id}/2058a", response_model=Form2058AResponse)
def get_2058a(
    exercice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_form(exercice_id, current_user, db)


@router.put("/{exercice_id}/2058a", response_model=Form2058AResponse)
def save_2058a(
    exercice_id: int,
    data: Form2058AData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = _get_form(exercice_id, current_user, db)
    for field, value in data.model_dump().items():
        setattr(form, field, value)
    # Auto-calculate totals on save
    result = calculate_2058a(form)
    form.ws_total_reintegrations = result["ws_total_reintegrations"]
    form.wt_total_deductions = result["wt_total_deductions"]
    form.wu_resultat_fiscal = result["wu_resultat_fiscal"]
    db.commit()
    db.refresh(form)
    return form


@router.post("/{exercice_id}/2058a/calculate", response_model=CalculationResult)
def calculate(
    exercice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = _get_form(exercice_id, current_user, db)
    result = calculate_2058a(form)
    # Persist calculated totals
    form.ws_total_reintegrations = result["ws_total_reintegrations"]
    form.wt_total_deductions = result["wt_total_deductions"]
    form.wu_resultat_fiscal = result["wu_resultat_fiscal"]
    db.commit()
    return CalculationResult(**result)


@router.post("/{exercice_id}/2058a/validate", response_model=ValidationResult)
def validate(
    exercice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = _get_form(exercice_id, current_user, db)
    messages = validate_2058a(form)
    has_errors = any(m.niveau == "erreur" for m in messages)
    return ValidationResult(valide=not has_errors, messages=messages)
