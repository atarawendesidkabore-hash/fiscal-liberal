"""Auth integration tests for FiscIA Pro JWT + RBAC."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fiscia.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    has_role,
)
from fiscia.database import Base
from fiscia.models_db import Firm, TokenBlacklist, User


# --- Unit tests (no DB needed) ---

class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("SecurePass123!")
        assert hashed != "SecurePass123!"
        assert verify_password("SecurePass123!", hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("SecurePass123!")
        assert not verify_password("WrongPass", hashed)


class TestJWT:
    def test_create_and_decode_access_token(self):
        token = create_access_token("user-1", "test@example.com", "admin", "firm-1")
        payload = decode_token(token)
        assert payload["sub"] == "user-1"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["firm_id"] == "firm-1"
        assert payload["type"] == "access"

    def test_create_and_decode_refresh_token(self):
        token = create_refresh_token("user-1")
        payload = decode_token(token)
        assert payload["sub"] == "user-1"
        assert payload["type"] == "refresh"

    def test_expired_token_raises(self):
        import jwt as pyjwt
        from fiscia.auth import SECRET_KEY, ALGORITHM
        from datetime import datetime, timedelta, timezone

        payload = {
            "sub": "user-1",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = pyjwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_token(token)

    def test_invalid_token_raises(self):
        import jwt as pyjwt
        with pytest.raises(pyjwt.PyJWTError):
            decode_token("not.a.valid.token")


class TestRBAC:
    def test_admin_has_all_roles(self):
        assert has_role("admin", "admin")
        assert has_role("admin", "fiscaliste")
        assert has_role("admin", "client")

    def test_fiscaliste_has_fiscaliste_and_client(self):
        assert has_role("fiscaliste", "fiscaliste")
        assert has_role("fiscaliste", "client")
        assert not has_role("fiscaliste", "admin")

    def test_client_only_has_client(self):
        assert has_role("client", "client")
        assert not has_role("client", "fiscaliste")
        assert not has_role("client", "admin")

    def test_unknown_role_has_nothing(self):
        assert not has_role("unknown", "client")


# --- Integration tests (async DB) ---

@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_user_with_firm(async_db):
    """Creating a firm + admin user."""
    firm = Firm(name="Cabinet Dupont", siren="123456789")
    async_db.add(firm)
    await async_db.flush()

    user = User(
        email="admin@dupont.fr",
        hashed_password=hash_password("AdminPass1!"),
        full_name="Jean Dupont",
        role="admin",
        firm_id=firm.id,
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)

    assert user.id is not None
    assert user.role == "admin"
    assert user.firm_id == firm.id


@pytest.mark.asyncio
async def test_user_password_verification(async_db):
    """Stored password can be verified."""
    user = User(
        email="fiscaliste@test.fr",
        hashed_password=hash_password("FiscPass99!"),
        role="fiscaliste",
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)

    assert verify_password("FiscPass99!", user.hashed_password)
    assert not verify_password("WrongPass", user.hashed_password)


@pytest.mark.asyncio
async def test_token_blacklist(async_db):
    """Blacklisted JTI is stored and retrievable."""
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import select

    entry = TokenBlacklist(
        jti="test-jti-001",
        user_id="user-1",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    async_db.add(entry)
    await async_db.commit()

    result = await async_db.execute(
        select(TokenBlacklist).where(TokenBlacklist.jti == "test-jti-001")
    )
    found = result.scalar_one_or_none()
    assert found is not None
    assert found.user_id == "user-1"


@pytest.mark.asyncio
async def test_firm_data_isolation(async_db):
    """Users from different firms cannot see each other's data."""
    from sqlalchemy import select

    firm_a = Firm(name="Cabinet A")
    firm_b = Firm(name="Cabinet B")
    async_db.add_all([firm_a, firm_b])
    await async_db.flush()

    user_a = User(email="a@a.fr", hashed_password=hash_password("Pass1234!"), role="admin", firm_id=firm_a.id)
    user_b = User(email="b@b.fr", hashed_password=hash_password("Pass1234!"), role="admin", firm_id=firm_b.id)
    async_db.add_all([user_a, user_b])
    await async_db.commit()

    # Query users scoped to firm A
    result = await async_db.execute(select(User).where(User.firm_id == firm_a.id))
    firm_a_users = result.scalars().all()
    assert len(firm_a_users) == 1
    assert firm_a_users[0].email == "a@a.fr"

    # Query users scoped to firm B
    result = await async_db.execute(select(User).where(User.firm_id == firm_b.id))
    firm_b_users = result.scalars().all()
    assert len(firm_b_users) == 1
    assert firm_b_users[0].email == "b@b.fr"


@pytest.mark.asyncio
async def test_token_refresh_rotation(async_db):
    """Refresh token rotation: old token gets blacklisted, new pair issued."""
    from fiscia.auth import blacklist_entry
    from datetime import datetime, timezone
    from sqlalchemy import select

    # Create initial refresh token
    refresh = create_refresh_token("user-1")
    payload = decode_token(refresh)

    # Simulate rotation: blacklist old token
    entry = blacklist_entry(
        jti=payload["jti"],
        user_id="user-1",
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
    )
    async_db.add(entry)
    await async_db.commit()

    # Old token JTI should be in blacklist
    result = await async_db.execute(
        select(TokenBlacklist).where(TokenBlacklist.jti == payload["jti"])
    )
    assert result.scalar_one_or_none() is not None

    # New refresh token should have a different JTI
    new_refresh = create_refresh_token("user-1")
    new_payload = decode_token(new_refresh)
    assert new_payload["jti"] != payload["jti"]
