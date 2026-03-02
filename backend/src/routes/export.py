from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from src.database.connection import get_db
from src.database.models import (
    User, Exercice, Company, Form2058A, Form2058B, Form2058BItem, Form2058C,
)
from src.services.pdf_generator import generate_2058a_pdf, generate_2058b_pdf, generate_2058c_pdf
from src.utils.security import get_current_user

router = APIRouter()


def _get_exercice_and_company(exercice_id: int, user: User, db: Session):
    exercice = db.query(Exercice).filter(Exercice.id == exercice_id).first()
    if not exercice:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    company = db.query(Company).filter(
        Company.id == exercice.company_id, Company.user_id == user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Société introuvable")
    return exercice, company


@router.post("/{exercice_id}/export/pdf")
def export_pdf(
    exercice_id: int,
    formulaire: str = Query("2058a", description="Formulaire à exporter : 2058a, 2058b, 2058c"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercice, company = _get_exercice_and_company(exercice_id, current_user, db)

    if formulaire == "2058a":
        form = db.query(Form2058A).filter(Form2058A.exercice_id == exercice_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Formulaire 2058-A introuvable")
        pdf_bytes = generate_2058a_pdf(form, exercice, company)
        filename = f"2058A_{company.siren or 'XXXX'}_{exercice.date_fin}.pdf"

    elif formulaire == "2058b":
        form = db.query(Form2058B).filter(Form2058B.exercice_id == exercice_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Formulaire 2058-B introuvable")
        items = db.query(Form2058BItem).filter(Form2058BItem.form_2058b_id == form.id).all()
        pdf_bytes = generate_2058b_pdf(form, items, exercice, company)
        filename = f"2058B_{company.siren or 'XXXX'}_{exercice.date_fin}.pdf"

    elif formulaire == "2058c":
        form = db.query(Form2058C).filter(Form2058C.exercice_id == exercice_id).first()
        if not form:
            raise HTTPException(status_code=404, detail="Formulaire 2058-C introuvable")
        pdf_bytes = generate_2058c_pdf(form, exercice, company)
        filename = f"2058C_{company.siren or 'XXXX'}_{exercice.date_fin}.pdf"

    else:
        raise HTTPException(status_code=400, detail="Formulaire inconnu. Utilisez 2058a, 2058b, ou 2058c.")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
