from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import Select, delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.models_db import LiasseCalculation


class RepositoryError(RuntimeError):
    pass


@dataclass(slots=True)
class Pagination:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return max(self.page - 1, 0) * self.page_size


class CalculationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        user_id: int | None,
        firm_id: int | None = None,
        siren: str,
        exercice_clos: date,
        input_json: dict[str, Any],
        result_json: dict[str, Any],
    ) -> LiasseCalculation:
        calc = LiasseCalculation(
            user_id=user_id,
            firm_id=firm_id,
            siren=siren,
            exercice_clos=exercice_clos,
            input_json=input_json,
            result_json=result_json,
        )
        try:
            self.session.add(calc)
            if hasattr(self.session, "commit"):
                await self.session.commit()
            elif hasattr(self.session, "begin"):
                async with self.session.begin():
                    pass
            await self.session.refresh(calc)
            return calc
        except SQLAlchemyError as exc:
            if hasattr(self.session, "rollback"):
                await self.session.rollback()
            raise RepositoryError(f"Unable to create calculation: {exc}") from exc

    async def get_by_id(self, calculation_id: int) -> LiasseCalculation | None:
        try:
            stmt = select(LiasseCalculation).where(LiasseCalculation.id == calculation_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise RepositoryError(f"Unable to fetch calculation {calculation_id}: {exc}") from exc

    async def list(
        self,
        *,
        user_id: int | None = None,
        siren: str | None = None,
        exercice_from: date | None = None,
        exercice_to: date | None = None,
        pagination: Pagination | None = None,
        sort_desc: bool = True,
    ) -> dict[str, Any]:
        page = pagination or Pagination()
        try:
            base_stmt: Select[tuple[LiasseCalculation]] = select(LiasseCalculation)
            count_stmt = select(func.count(LiasseCalculation.id))

            if user_id is not None:
                base_stmt = base_stmt.where(LiasseCalculation.user_id == user_id)
                count_stmt = count_stmt.where(LiasseCalculation.user_id == user_id)
            if siren is not None:
                base_stmt = base_stmt.where(LiasseCalculation.siren == siren)
                count_stmt = count_stmt.where(LiasseCalculation.siren == siren)
            if exercice_from is not None:
                base_stmt = base_stmt.where(LiasseCalculation.exercice_clos >= exercice_from)
                count_stmt = count_stmt.where(LiasseCalculation.exercice_clos >= exercice_from)
            if exercice_to is not None:
                base_stmt = base_stmt.where(LiasseCalculation.exercice_clos <= exercice_to)
                count_stmt = count_stmt.where(LiasseCalculation.exercice_clos <= exercice_to)

            order_col = LiasseCalculation.created_at.desc() if sort_desc else LiasseCalculation.created_at.asc()
            base_stmt = base_stmt.order_by(order_col).offset(page.offset).limit(page.page_size)

            total_result = await self.session.execute(count_stmt)
            total = total_result.scalar_one()

            rows = await self.session.execute(base_stmt)
            items = list(rows.scalars().all())
            return {"items": items, "total": total, "page": page.page, "page_size": page.page_size}
        except SQLAlchemyError as exc:
            raise RepositoryError(f"Unable to list calculations: {exc}") from exc

    async def delete(self, calculation_id: int) -> bool:
        try:
            result = await self.session.execute(delete(LiasseCalculation).where(LiasseCalculation.id == calculation_id))
            if hasattr(self.session, "commit"):
                await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as exc:
            if hasattr(self.session, "rollback"):
                await self.session.rollback()
            raise RepositoryError(f"Unable to delete calculation {calculation_id}: {exc}") from exc
