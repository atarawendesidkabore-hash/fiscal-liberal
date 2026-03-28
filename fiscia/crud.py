"""
CRUD operations for FiscIA Pro persistence layer.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from fiscia.models_db import LiasseCalculation


def create_liasse_calculation(
    db: Session,
    user_id: Optional[str],
    siren: str,
    exercice_clos: str,
    input_data: dict,
    result_data: dict,
) -> LiasseCalculation:
    """Create and persist a new liasse calculation."""
    record = LiasseCalculation(
        user_id=user_id,
        siren=siren,
        exercice_clos=exercice_clos,
        input_data=input_data,
        result_data=result_data,
        rf_brut=result_data.get("rf_brut", 0),
        rf_net=result_data.get("rf_net", 0),
        is_total=result_data.get("is_total", 0),
        regime=result_data.get("regime", ""),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_liasse_calculation(
    db: Session,
    liasse_id: str,
    user_id: Optional[str] = None,
) -> Optional[LiasseCalculation]:
    """Retrieve a liasse calculation by ID, optionally scoped to a user."""
    stmt = select(LiasseCalculation).where(LiasseCalculation.id == liasse_id)
    if user_id is not None:
        stmt = stmt.where(LiasseCalculation.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def list_liasse_calculations(
    db: Session,
    user_id: Optional[str] = None,
    siren: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[LiasseCalculation]:
    """List liasse calculations with optional filters."""
    stmt = select(LiasseCalculation).order_by(LiasseCalculation.created_at.desc())
    if user_id is not None:
        stmt = stmt.where(LiasseCalculation.user_id == user_id)
    if siren is not None:
        stmt = stmt.where(LiasseCalculation.siren == siren)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def delete_liasse_calculation(
    db: Session,
    liasse_id: str,
    user_id: Optional[str] = None,
) -> bool:
    """Delete a liasse calculation. Returns True if found and deleted."""
    record = get_liasse_calculation(db, liasse_id, user_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True
