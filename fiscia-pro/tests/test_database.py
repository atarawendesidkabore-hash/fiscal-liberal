from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path

from fiscia.models_db import Base, LiasseCalculation
from fiscia.repositories.calculations import CalculationRepository


class _BeginCtx:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _ScalarRows:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _ExecuteResult:
    def __init__(self, *, count=None, rows=None, rowcount=0):
        self._count = count
        self._rows = rows or []
        self.rowcount = rowcount

    def scalar_one(self):
        return self._count

    def scalar_one_or_none(self):
        return self._rows[0] if self._rows else None

    def scalars(self):
        return _ScalarRows(self._rows)


class FakeAsyncSession:
    def __init__(self):
        self.storage: list[LiasseCalculation] = []
        self._next_id = 1

    def begin(self):
        return _BeginCtx()

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._next_id
            self._next_id += 1
        self.storage.append(obj)

    async def refresh(self, _obj):
        return None

    async def execute(self, statement):
        sql = str(statement).lower()
        if "count(" in sql:
            return _ExecuteResult(count=len(self.storage))
        if "delete from" in sql:
            if self.storage:
                self.storage.pop()
                return _ExecuteResult(rowcount=1)
            return _ExecuteResult(rowcount=0)
        return _ExecuteResult(rows=list(self.storage))


def test_models_db_tables_present():
    """Schema metadata should expose the expected core tables."""
    tables = set(Base.metadata.tables.keys())
    assert {"users", "liasse_calculations", "audit_logs"}.issubset(tables)


def test_migration_script_exists_and_contains_core_schema():
    """Initial Alembic migration must declare core tables."""
    migration = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "001_initial_migration.py"
    )
    assert migration.exists()
    content = migration.read_text(encoding="utf-8")
    assert "create_table(" in content
    assert "users" in content
    assert "liasse_calculations" in content
    assert "audit_logs" in content


def test_repository_crud_with_fake_async_session():
    """Repository operations should work with async session contract."""

    async def run():
        session = FakeAsyncSession()
        repo = CalculationRepository(session)

        calc = await repo.create(
            user_id=1,
            siren="123456789",
            exercice_clos=date(2024, 12, 31),
            input_json={"wi_is_comptabilise": "1000"},
            result_json={"is_total": "25000.00"},
        )
        assert calc.id == 1

        listing = await repo.list(user_id=1)
        assert listing["total"] == 1
        assert len(listing["items"]) == 1

        deleted = await repo.delete(calc.id)
        assert deleted is True

    asyncio.run(run())


def test_concurrent_repository_access():
    """Concurrent creates should complete without data corruption."""

    async def run():
        session = FakeAsyncSession()
        repo = CalculationRepository(session)

        async def create_one(i: int):
            return await repo.create(
                user_id=1,
                siren="123456789",
                exercice_clos=date(2024, 12, 31),
                input_json={"request_id": i},
                result_json={"status": "ok"},
            )

        rows = await asyncio.gather(*[create_one(i) for i in range(10)])
        assert len(rows) == 10
        assert len({row.id for row in rows}) == 10

    asyncio.run(run())

