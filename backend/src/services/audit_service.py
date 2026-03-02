"""
Service d'audit — enregistre les modifications sur les formulaires fiscaux.
"""

from sqlalchemy.orm import Session

from src.database.models import AuditLog


def log_change(
    db: Session,
    user_id: int,
    exercice_id: int,
    form_type: str,
    field_changed: str,
    old_value: str,
    new_value: str,
    ip_address: str = "",
):
    entry = AuditLog(
        user_id=user_id,
        exercice_id=exercice_id,
        form_type=form_type,
        field_changed=field_changed,
        old_value=str(old_value),
        new_value=str(new_value),
        ip_address=ip_address,
    )
    db.add(entry)
