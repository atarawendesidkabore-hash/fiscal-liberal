"""Database integration tests for FiscIA Pro persistence layer."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fiscia.database import Base
from fiscia.crud import (
    create_liasse_calculation,
    delete_liasse_calculation,
    get_liasse_calculation,
    list_liasse_calculations,
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


SAMPLE_INPUT = {
    "siren": "123456789",
    "exercice_clos": "2024-12-31",
    "benefice_comptable": 120000,
    "wi_is_comptabilise": 10000,
    "wg_amendes_penalites": 2000,
}

SAMPLE_RESULT = {
    "rf_brut": 115000.0,
    "rf_net": 115000.0,
    "is_total": 24500.0,
    "regime": "PME - Taux reduit Art. 219-I-b CGI",
    "acompte_trimestriel": 6125.0,
}


def test_create_liasse_calculation(db_session):
    """Create a liasse calculation and verify it's persisted."""
    record = create_liasse_calculation(
        db=db_session,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    assert record.id is not None
    assert record.siren == "123456789"
    assert record.is_total == 24500.0
    assert record.regime == "PME - Taux reduit Art. 219-I-b CGI"


def test_get_liasse_calculation(db_session):
    """Retrieve a specific calculation by ID."""
    record = create_liasse_calculation(
        db=db_session,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    fetched = get_liasse_calculation(db_session, record.id)
    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.input_data == SAMPLE_INPUT
    assert fetched.result_data == SAMPLE_RESULT


def test_get_liasse_scoped_to_user(db_session):
    """Scoped retrieval: wrong user_id returns None."""
    record = create_liasse_calculation(
        db=db_session,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    assert get_liasse_calculation(db_session, record.id, user_id="user-001") is not None
    assert get_liasse_calculation(db_session, record.id, user_id="user-999") is None


def test_list_liasse_calculations(db_session):
    """List calculations with optional filters."""
    for i in range(3):
        create_liasse_calculation(
            db=db_session,
            user_id="user-001",
            siren=f"12345678{i}",
            exercice_clos="2024-12-31",
            input_data=SAMPLE_INPUT,
            result_data=SAMPLE_RESULT,
        )
    create_liasse_calculation(
        db=db_session,
        user_id="user-002",
        siren="987654321",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )

    all_records = list_liasse_calculations(db_session)
    assert len(all_records) == 4

    user1_records = list_liasse_calculations(db_session, user_id="user-001")
    assert len(user1_records) == 3

    siren_records = list_liasse_calculations(db_session, siren="987654321")
    assert len(siren_records) == 1


def test_list_pagination(db_session):
    """Verify skip/limit pagination."""
    for i in range(5):
        create_liasse_calculation(
            db=db_session,
            user_id="user-001",
            siren=f"12345678{i}",
            exercice_clos="2024-12-31",
            input_data=SAMPLE_INPUT,
            result_data=SAMPLE_RESULT,
        )
    page = list_liasse_calculations(db_session, skip=2, limit=2)
    assert len(page) == 2


def test_delete_liasse_calculation(db_session):
    """Delete a calculation and verify it's gone."""
    record = create_liasse_calculation(
        db=db_session,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    assert delete_liasse_calculation(db_session, record.id) is True
    assert get_liasse_calculation(db_session, record.id) is None


def test_delete_nonexistent(db_session):
    """Deleting a nonexistent record returns False."""
    assert delete_liasse_calculation(db_session, "nonexistent-id") is False


def test_delete_scoped_to_user(db_session):
    """Cannot delete another user's calculation."""
    record = create_liasse_calculation(
        db=db_session,
        user_id="user-001",
        siren="123456789",
        exercice_clos="2024-12-31",
        input_data=SAMPLE_INPUT,
        result_data=SAMPLE_RESULT,
    )
    assert delete_liasse_calculation(db_session, record.id, user_id="user-999") is False
    assert get_liasse_calculation(db_session, record.id) is not None
