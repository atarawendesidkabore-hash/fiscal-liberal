"""
Database engine, session factory, and health check for FiscIA Pro.
Supports PostgreSQL (production) and SQLite (dev/test).
"""
import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "fiscia.db"


def _default_database_url() -> str:
    """Use a repo-stable SQLite path so cwd never changes the active database."""
    return f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"


DATABASE_URL = os.environ.get("DATABASE_URL", _default_database_url())

# Use check_same_thread only for SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for use outside FastAPI (CLI, scripts)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_health() -> dict:
    """Check that the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def create_all_tables():
    """Create all tables defined in models_db.py. Used for dev/test."""
    from fiscia import billing_models as _billing_models  # noqa: F401
    from fiscia import models_db as _models_db  # noqa: F401

    Base.metadata.create_all(bind=engine)
