from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

DEFAULT_DATABASE_URL = "postgresql+asyncpg://fiscia:fiscia@postgres:5432/fiscia"

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def _engine_kwargs_for_url(database_url: str) -> dict:
    common = {
        "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
        "pool_pre_ping": True,
    }
    if database_url.startswith("sqlite+"):
        # SQLite async dialect does not support pool_size/max_overflow arguments.
        return common
    common.update(
        {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
        }
    )
    return common


def get_async_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        database_url = get_database_url()
        _engine = create_async_engine(
            database_url,
            **_engine_kwargs_for_url(database_url),
        )
    return _engine


def get_engine() -> AsyncEngine:
    # Backward-compatible alias.
    return get_async_engine()


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_async_engine(), expire_on_commit=False)
    return _session_factory


@asynccontextmanager
async def db_session_context() -> AsyncGenerator[AsyncSession, None]:
    session = get_async_session_factory()()
    try:
        yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    # Backward-compatible dependency hook used by existing endpoints.
    async with db_session_context() as session:
        yield session


async def database_health_check() -> dict:
    try:
        async with db_session_context() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except Exception as exc:
        return {"status": "error", "database": "unreachable", "detail": str(exc)}


async def dispose_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


def reset_engine_state_for_tests() -> None:
    """Utility hook for tests that need deterministic singleton behavior."""
    global _engine, _session_factory
    _engine = None
    _session_factory = None
