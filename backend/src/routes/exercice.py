from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User, Company, Exercice, Form2058A, Form2058B, Form2058C
from src.schemas.exercice import ExerciceCreate, ExerciceUpdate, ExerciceResponse
from src.utils.security import get_current_user

router = APIRouter()


def _check_company_owner(db: Session, company_id: int, user_id: int) -> Company:
    company = db.query(Company).filter(
        Company.id == company_id, Company.user_id == user_id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Société introuvable")
    return company


@router.get("/by-company/{company_id}", response_model=List[ExerciceResponse])
def list_exercices(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_company_owner(db, company_id, current_user.id)
    return db.query(Exercice).filter(Exercice.company_id == company_id).order_by(Exercice.date_debut.desc()).all()


@router.post("", response_model=ExerciceResponse, status_code=201)
def create_exercice(
    data: ExerciceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_company_owner(db, data.company_id, current_user.id)
    exercice = Exercice(**data.model_dump())
    db.add(exercice)
    db.flush()

    # Créer automatiquement les formulaires vides
    db.add(Form2058A(exercice_id=exercice.id))
    db.add(Form2058B(exercice_id=exercice.id))
    db.add(Form2058C(exercice_id=exercice.id))

    db.commit()
    db.refresh(exercice)
    return exercice


@router.get("/{exercice_id}", response_model=ExerciceResponse)
def get_exercice(
    exercice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercice = db.query(Exercice).filter(Exercice.id == exercice_id).first()
    if not exercice:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    _check_company_owner(db, exercice.company_id, current_user.id)
    return exercice


@router.put("/{exercice_id}", response_model=ExerciceResponse)
def update_exercice(
    exercice_id: int,
    data: ExerciceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercice = db.query(Exercice).filter(Exercice.id == exercice_id).first()
    if not exercice:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    _check_company_owner(db, exercice.company_id, current_user.id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exercice, field, value)
    db.commit()
    db.refresh(exercice)
    return exercice
