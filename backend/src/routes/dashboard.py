from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User, Company, Exercice, Form2058A
from src.utils.security import get_current_user

router = APIRouter()


@router.get("/{company_id}")
def get_dashboard(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(
        Company.id == company_id, Company.user_id == current_user.id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Société introuvable")

    exercices = (
        db.query(Exercice)
        .filter(Exercice.company_id == company_id)
        .order_by(Exercice.date_debut.asc())
        .all()
    )

    historique = []
    for ex in exercices:
        form = db.query(Form2058A).filter(Form2058A.exercice_id == ex.id).first()
        entry = {
            "exercice_id": ex.id,
            "periode": f"{ex.date_debut} — {ex.date_fin}",
            "statut": ex.statut,
            "resultat_comptable": form.wa_resultat_comptable if form else 0.0,
            "total_reintegrations": form.ws_total_reintegrations if form else 0.0,
            "total_deductions": form.wt_total_deductions if form else 0.0,
            "resultat_fiscal": form.wu_resultat_fiscal if form else 0.0,
        }
        historique.append(entry)

    # Résumé
    dernier = historique[-1] if historique else None
    return {
        "company": {
            "id": company.id,
            "raison_sociale": company.raison_sociale,
            "forme_juridique": company.forme_juridique,
            "siren": company.siren,
        },
        "nb_exercices": len(exercices),
        "dernier_exercice": dernier,
        "historique": historique,
    }
