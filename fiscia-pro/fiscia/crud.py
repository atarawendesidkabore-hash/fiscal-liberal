from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.models_db import AuditLog, LiasseCalculation
from fiscia.repositories.calculations import CalculationRepository, Pagination, RepositoryError


class CrudError(RuntimeError):
    pass


async def create_calculation(
    session: AsyncSession,
    *,
    user_id: int | None,
    firm_id: int | None = None,
    siren: str,
    exercice_clos: date,
    input_json: dict[str, Any],
    result_json: dict[str, Any],
) -> LiasseCalculation:
    try:
        repo = CalculationRepository(session)
        return await repo.create(
            user_id=user_id,
            firm_id=firm_id,
            siren=siren,
            exercice_clos=exercice_clos,
            input_json=input_json,
            result_json=result_json,
        )
    except RepositoryError as exc:
        raise CrudError(str(exc)) from exc


async def get_calculation(session: AsyncSession, calculation_id: int) -> LiasseCalculation | None:
    try:
        repo = CalculationRepository(session)
        return await repo.get_by_id(calculation_id)
    except RepositoryError as exc:
        raise CrudError(str(exc)) from exc


async def list_calculations(
    session: AsyncSession,
    *,
    user_id: int | None = None,
    siren: str | None = None,
    exercice_from: date | None = None,
    exercice_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_desc: bool = True,
) -> dict[str, Any]:
    try:
        repo = CalculationRepository(session)
        return await repo.list(
            user_id=user_id,
            siren=siren,
            exercice_from=exercice_from,
            exercice_to=exercice_to,
            pagination=Pagination(page=page, page_size=page_size),
            sort_desc=sort_desc,
        )
    except RepositoryError as exc:
        raise CrudError(str(exc)) from exc


async def delete_calculation(session: AsyncSession, calculation_id: int) -> bool:
    try:
        repo = CalculationRepository(session)
        return await repo.delete(calculation_id)
    except RepositoryError as exc:
        raise CrudError(str(exc)) from exc


async def create_audit_log(
    session: AsyncSession,
    *,
    user_id: int | None,
    firm_id: int | None = None,
    action: str,
    resource_type: str | None = None,
    resource_id: int | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        firm_id=firm_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    try:
        session.add(log)
        if hasattr(session, "commit"):
            await session.commit()
        elif hasattr(session, "begin"):
            async with session.begin():
                pass
        await session.refresh(log)
        return log
    except SQLAlchemyError as exc:
        if hasattr(session, "rollback"):
            await session.rollback()
        raise CrudError(f"Unable to create audit log: {exc}") from exc
