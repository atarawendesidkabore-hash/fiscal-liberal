from __future__ import annotations

import asyncio
from datetime import date
from typing import Any

from fiscia import database
from fiscia.crud import create_audit_log, create_calculation


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
    def __init__(self, *, count: int = 0, rows: list[Any] | None = None, rowcount: int = 0):
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
        self.calculations = []
        self.audit_logs = []
        self._next_id = 1
        self.closed = False

    def begin(self):
        return _BeginCtx()

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._next_id
            self._next_id += 1
        if hasattr(obj, "siren"):
            self.calculations.append(obj)
        else:
            self.audit_logs.append(obj)

    async def refresh(self, _obj):
        return None

    async def execute(self, statement):
        sql = str(statement).lower()
        if "count(" in sql:
            return _ExecuteResult(count=len(self.calculations))
        if "delete from" in sql:
            if self.calculations:
                self.calculations.pop()
                return _ExecuteResult(rowcount=1)
            return _ExecuteResult(rowcount=0)
        return _ExecuteResult(rows=list(self.calculations))

    async def rollback(self):
        return None

    async def close(self):
        self.closed = True


def test_async_engine_singleton_and_pool_config(monkeypatch):
    """Concurrent calls must reuse one engine and keep pool kwargs."""
    calls: list[dict[str, Any]] = []

    class FakeEngine:
        async def dispose(self):
            return None

    def fake_create_async_engine(url: str, **kwargs):
        calls.append({"url": url, "kwargs": kwargs})
        return FakeEngine()

    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@db:5432/x")
    monkeypatch.setenv("DB_POOL_SIZE", "9")
    monkeypatch.setenv("DB_MAX_OVERFLOW", "15")
    monkeypatch.setattr(database, "create_async_engine", fake_create_async_engine)
    database.reset_engine_state_for_tests()

    async def worker():
        return id(database.get_async_engine())

    async def run():
        return await asyncio.gather(*[worker() for _ in range(20)])

    ids = asyncio.run(run())
    assert len(set(ids)) == 1
    assert len(calls) == 1
    assert calls[0]["kwargs"]["pool_size"] == 9
    assert calls[0]["kwargs"]["max_overflow"] == 15


def test_async_db_session_dependency(monkeypatch):
    """Dependency should yield session and close it once done."""
    fake_session = FakeAsyncSession()

    class Factory:
        def __call__(self):
            return fake_session

    monkeypatch.setattr(database, "get_async_session_factory", lambda: Factory())
    database.reset_engine_state_for_tests()

    async def run():
        gen = database.get_db_session()
        session = await gen.__anext__()
        assert session is fake_session
        await gen.aclose()
        assert fake_session.closed is True

    asyncio.run(run())


def test_async_crud_concurrent_user_simulation():
    """Simulate many concurrent users writing calculations and audit logs."""

    async def run():
        session = FakeAsyncSession()

        async def one_user(i: int):
            calc = await create_calculation(
                session,
                user_id=1,
                siren="123456789",
                exercice_clos=date(2024, 12, 31),
                input_json={"request_id": i},
                result_json={"is_total": "25000.00"},
            )
            await create_audit_log(
                session=session,
                user_id=1,
                action="create_calculation",
                resource_type="liasse",
                resource_id=calc.id,
                details={"request_id": i},
            )
            return calc.id

        ids = await asyncio.gather(*[one_user(i) for i in range(30)])
        assert len(ids) == 30
        assert len(set(ids)) == 30
        assert len(session.calculations) == 30
        assert len(session.audit_logs) == 30

    asyncio.run(run())
