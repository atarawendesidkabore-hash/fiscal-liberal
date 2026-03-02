from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User, Exercice, Company, Form2058B, Form2058BItem
from src.schemas.forms import Form2058BItemCreate, Form2058BItemResponse, Form2058BResponse
from src.utils.security import get_current_user

router = APIRouter()


def _get_form_b(exercice_id: int, user: User, db: Session) -> Form2058B:
    exercice = db.query(Exercice).filter(Exercice.id == exercice_id).first()
    if not exercice:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    company = db.query(Company).filter(
        Company.id == exercice.company_id, Company.user_id == user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Société introuvable")
    form = db.query(Form2058B).filter(Form2058B.exercice_id == exercice_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulaire 2058-B introuvable")
    return form


@router.get("/{exercice_id}/2058b")
def get_2058b(
    exercice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = _get_form_b(exercice_id, current_user, db)
    items = db.query(Form2058BItem).filter(Form2058BItem.form_2058b_id == form.id).all()
    total = sum(item.montant for item in items)
    return {
        "id": form.id,
        "exercice_id": form.exercice_id,
        "items": [Form2058BItemResponse.model_validate(i) for i in items],
        "total": round(total, 2),
        "updated_at": form.updated_at,
    }


@router.post("/{exercice_id}/2058b/items", response_model=Form2058BItemResponse, status_code=201)
def add_item(
    exercice_id: int,
    data: Form2058BItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = _get_form_b(exercice_id, current_user, db)
    item = Form2058BItem(form_2058b_id=form.id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{exercice_id}/2058b/items/{item_id}", status_code=204)
def delete_item(
    exercice_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = _get_form_b(exercice_id, current_user, db)
    item = db.query(Form2058BItem).filter(
        Form2058BItem.id == item_id, Form2058BItem.form_2058b_id == form.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ligne introuvable")
    db.delete(item)
    db.commit()
