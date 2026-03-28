"""
Async database engine and session factory for FiscIA Pro.
Uses aiosqlite (dev/test) or asyncpg (production PostgreSQL).

Coexists with the sync database.py — endpoints can migrate
to async incrementally without breaking existing sync code.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from fiscia.database import DATABASE_URL

# Convert sync URLs to async driver URLs
if DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
elif DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql+asyncpg://"):
    ASYNC_DATABASE_URL = DATABASE_URL
else:
    ASYNC_DATABASE_URL = DATABASE_URL

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_db():
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_async_database_health() -> dict:
    """Async health check for the database connection."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "driver": "async",
            "database": ASYNC_DATABASE_URL.split("@")[-1] if "@" in ASYNC_DATABASE_URL else "(local)",
        }
    except Exception as e:
        return {"status": "error", "driver": "async", "detail": str(e)}
