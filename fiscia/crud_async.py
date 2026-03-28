"""
Async CRUD operations + audit logging for FiscIA Pro.
Mirrors the sync crud.py but uses async sessions.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.models_db import AuditLog, LiasseCalculation


async def log_audit(
    db: AsyncSession,
    action: str,
    module: str,
    user_id: Optional[str] = None,
    siren: Optional[str] = None,
    detail: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Record an audit trail entry."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        module=module,
        siren=siren,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()
    return entry


async def async_create_liasse_calculation(
    db: AsyncSession,
    user_id: Optional[str],
    siren: str,
    exercice_clos: str,
    input_data: dict,
    result_data: dict,
    ip_address: Optional[str] = None,
) -> LiasseCalculation:
    """Create and persist a liasse calculation (async) with audit trail."""
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
    await db.flush()
    await db.refresh(record)

    await log_audit(
        db,
        action="create_liasse",
        module="liasse",
        user_id=user_id,
        siren=siren,
        detail={"liasse_id": record.id, "is_total": result_data.get("is_total", 0)},
        ip_address=ip_address,
    )
    await db.commit()
    return record


async def async_get_liasse_calculation(
    db: AsyncSession,
    liasse_id: str,
    user_id: Optional[str] = None,
) -> Optional[LiasseCalculation]:
    """Retrieve a liasse calculation by ID (async)."""
    stmt = select(LiasseCalculation).where(LiasseCalculation.id == liasse_id)
    if user_id is not None:
        stmt = stmt.where(LiasseCalculation.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def async_list_liasse_calculations(
    db: AsyncSession,
    user_id: Optional[str] = None,
    siren: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[LiasseCalculation]:
    """List liasse calculations with optional filters (async)."""
    stmt = select(LiasseCalculation).order_by(LiasseCalculation.created_at.desc())
    if user_id is not None:
        stmt = stmt.where(LiasseCalculation.user_id == user_id)
    if siren is not None:
        stmt = stmt.where(LiasseCalculation.siren == siren)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def async_delete_liasse_calculation(
    db: AsyncSession,
    liasse_id: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> bool:
    """Delete a liasse calculation (async) with audit trail."""
    record = await async_get_liasse_calculation(db, liasse_id, user_id)
    if record is None:
        return False

    await log_audit(
        db,
        action="delete_liasse",
        module="liasse",
        user_id=user_id,
        siren=record.siren,
        detail={"liasse_id": liasse_id},
        ip_address=ip_address,
    )
    await db.delete(record)
    await db.commit()
    return True


async def async_list_audit_logs(
    db: AsyncSession,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """List audit log entries (async)."""
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
    if user_id is not None:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if action is not None:
        stmt = stmt.where(AuditLog.action == action)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
