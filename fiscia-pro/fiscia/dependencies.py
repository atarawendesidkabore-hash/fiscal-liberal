from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.database import get_db_session
from fiscia.repositories.calculations import CalculationRepository


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


def get_calculation_repository(
    session: AsyncSession = Depends(get_async_db_session),
) -> CalculationRepository:
    return CalculationRepository(session)

