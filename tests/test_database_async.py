"""Async database integration tests for FiscIA Pro."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fiscia.database import Base
from fiscia.crud_async import (
    async_create_liasse_calculation,
    async_delete_liasse_calculation,
    async_get_liasse_calculation,
    async_list_liasse_calculations,
    async_list_audit_logs,
    log_audit,
)


@pytest_asyncio.fixture
async def async_db():
    """Create an async in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


SAMPLE_INPUT = {
    "siren": "123456789",
    "exercice_clos": "2024-12-31",
    "benefice_comptable": 120000,
    "wi_is_comptabilise": 10000,
}

SAMPLE_RESULT = {
    "rf_brut": 115000.0,
    "rf_net": 115000.0,
    "is_total": 24500.0,
    "regime": "PME - Taux reduit Art. 219-I-b CGI",
    "acompte_trimestriel": 6125.0,
}


@pytest.mark.asyncio
async def test_async_create_liasse(async_db):
    record = await async_create_liasse_calculation(
        db=async_db,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    assert record.id is not None
    assert record.siren == "123456789"
    assert record.is_total == 24500.0


@pytest.mark.asyncio
async def test_async_get_liasse(async_db):
    record = await async_create_liasse_calculation(
        db=async_db,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    fetched = await async_get_liasse_calculation(async_db, record.id)
    assert fetched is not None
    assert fetched.id == record.id


@pytest.mark.asyncio
async def test_async_get_scoped_to_user(async_db):
    record = await async_create_liasse_calculation(
        db=async_db,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    assert await async_get_liasse_calculation(async_db, record.id, user_id="user-001") is not None
    assert await async_get_liasse_calculation(async_db, record.id, user_id="user-999") is None


@pytest.mark.asyncio
async def test_async_list_liasse(async_db):
    for i in range(3):
        await async_create_liasse_calculation(
            db=async_db,
            user_id="user-001",
            siren=f"12345678{i}",
            exercice_clos="2024-12-31",
            input_data=SAMPLE_INPUT,
            result_data=SAMPLE_RESULT,
        )
    records = await async_list_liasse_calculations(async_db, user_id="user-001")
    assert len(records) == 3


@pytest.mark.asyncio
async def test_async_delete_liasse(async_db):
    record = await async_create_liasse_calculation(
        db=async_db,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    assert await async_delete_liasse_calculation(async_db, record.id) is True
    assert await async_get_liasse_calculation(async_db, record.id) is None


@pytest.mark.asyncio
async def test_async_delete_nonexistent(async_db):
    assert await async_delete_liasse_calculation(async_db, "nonexistent-id") is False


@pytest.mark.asyncio
async def test_audit_log_created_on_create(async_db):
    """Creating a liasse should produce an audit log entry."""
    await async_create_liasse_calculation(
        db=async_db,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    logs = await async_list_audit_logs(async_db, user_id="user-001", action="create_liasse")
    assert len(logs) == 1
    assert logs[0].module == "liasse"
    assert logs[0].siren == "123456789"


@pytest.mark.asyncio
async def test_audit_log_created_on_delete(async_db):
    """Deleting a liasse should produce an audit log entry."""
    record = await async_create_liasse_calculation(
        db=async_db,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    await async_delete_liasse_calculation(async_db, record.id, user_id="user-001")
    logs = await async_list_audit_logs(async_db, action="delete_liasse")
    assert len(logs) == 1


@pytest.mark.asyncio
async def test_log_audit_standalone(async_db):
    """log_audit can be used independently."""
    entry = await log_audit(
        async_db,
        action="test_action",
        module="test",
        user_id="user-999",
        detail={"key": "value"},
    )
    await async_db.commit()
    assert entry.id is not None
    assert entry.action == "test_action"

    logs = await async_list_audit_logs(async_db, action="test_action")
    assert len(logs) == 1
