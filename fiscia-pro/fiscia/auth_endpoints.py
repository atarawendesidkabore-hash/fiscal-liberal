from __future__ import annotations

import asyncio
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.auth_models import (
    AuthResponse,
    Firm,
    LoginRequest,
    RefreshRequest,
    RefreshToken,
    RegisterRequest,
    Role,
    TokenPair,
    User,
    UserOut,
    build_token_pair,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    validate_password_policy,
    verify_password,
)
from fiscia.crud import CrudError, create_audit_log
from fiscia.dependencies import get_async_db_session
from fiscia.rbac import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

_RATE_LIMIT_STATE: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_RATE_LIMIT_LOCK = asyncio.Lock()


def reset_auth_rate_limiter_for_tests() -> None:
    _RATE_LIMIT_STATE.clear()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _client_ip(request: Request) -> str:
    if request.client is None:
        return "unknown"
    return request.client.host or "unknown"


def _is_production() -> bool:
    env = os.getenv("APP_ENV", os.getenv("ENV", "development")).lower()
    return env in {"production", "prod"}


def _enforce_https_if_required(request: Request) -> None:
    if not _is_production():
        return
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    if proto.lower() != "https":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HTTPS is required in production.",
        )


async def _enforce_rate_limit(
    request: Request,
    *,
    action: str,
    limit: int,
    window_seconds: int = 60,
) -> None:
    now = time.time()
    key = (_client_ip(request), action)

    async with _RATE_LIMIT_LOCK:
        bucket = _RATE_LIMIT_STATE[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()

        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication requests. Please retry later.",
            )

        bucket.append(now)


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(func.lower(User.email) == email.lower())
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def _store_refresh_token(session: AsyncSession, *, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
    token_row = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
    session.add(token_row)
    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise
    await session.refresh(token_row)
    return token_row


async def _mark_refresh_token_revoked(session: AsyncSession, *, jti: str, user_id: int | None = None) -> bool:
    stmt = select(RefreshToken).where(RefreshToken.jti == jti)
    if user_id is not None:
        stmt = stmt.where(RefreshToken.user_id == user_id)

    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        return False

    if row.revoked_at is not None:
        return True

    row.revoked_at = datetime.now(timezone.utc)
    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise
    return True


async def _get_active_refresh_token(session: AsyncSession, *, jti: str, user_id: int) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.user_id == user_id)
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        return None
    if row.revoked_at is not None:
        return None
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        return None
    return row


def _build_auth_response(user: User, *, access_token: str, refresh_token: str) -> AuthResponse:
    user_data = UserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
        is_active=user.is_active,
        created_at=user.created_at,
    )
    return AuthResponse(user=user_data, tokens=build_token_pair(access_token=access_token, refresh_token=refresh_token))


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_db_session),
) -> AuthResponse:
    _enforce_https_if_required(request)
    await _enforce_rate_limit(request, action="register", limit=10)

    email = _normalize_email(payload.email)

    try:
        validate_password_policy(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    existing_user = await _get_user_by_email(session, email)
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

    firm = Firm(name=payload.firm_name.strip(), plan_type=payload.plan_type.strip().lower())
    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        role=Role.ADMIN.value,
        firm=firm,
        is_active=True,
    )

    try:
        session.add(firm)
        session.add(user)
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Firm or user already exists.") from exc
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable.") from exc

    await session.refresh(user)

    access_token, _, _ = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
    )
    refresh_token, refresh_jti, refresh_exp = create_refresh_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
    )

    try:
        await _store_refresh_token(session, user_id=user.id, jti=refresh_jti, expires_at=refresh_exp)
        await create_audit_log(
            session=session,
            user_id=user.id,
            action="register",
            resource_type="user",
            resource_id=user.id,
            details={"firm_id": user.firm_id, "email": user.email},
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            firm_id=user.firm_id,
        )
    except (CrudError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to persist auth state.") from exc

    return _build_auth_response(user, access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_db_session),
) -> AuthResponse:
    _enforce_https_if_required(request)
    await _enforce_rate_limit(request, action="login", limit=20)

    email = _normalize_email(payload.email)
    user = await _get_user_by_email(session, email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user.")

    access_token, _, _ = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
    )
    refresh_token, refresh_jti, refresh_exp = create_refresh_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
    )

    try:
        await _store_refresh_token(session, user_id=user.id, jti=refresh_jti, expires_at=refresh_exp)
        await create_audit_log(
            session=session,
            user_id=user.id,
            action="login",
            resource_type="user",
            resource_id=user.id,
            details={"firm_id": user.firm_id},
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            firm_id=user.firm_id,
        )
    except (CrudError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to persist auth state.") from exc

    return _build_auth_response(user, access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_async_db_session),
) -> TokenPair:
    _enforce_https_if_required(request)
    await _enforce_rate_limit(request, action="refresh", limit=30)

    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.") from exc

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required.")

    try:
        user_id = int(decoded.get("sub"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token subject.") from exc

    jti = decoded.get("jti")
    if not isinstance(jti, str) or not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token identifier.")

    active_refresh = await _get_active_refresh_token(session, jti=jti, user_id=user_id)
    if active_refresh is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or expired.")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not available.")

    access_token, _, _ = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
    )
    new_refresh_token, new_refresh_jti, new_refresh_exp = create_refresh_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
    )

    try:
        active_refresh.revoked_at = datetime.now(timezone.utc)
        session.add(RefreshToken(user_id=user.id, jti=new_refresh_jti, expires_at=new_refresh_exp))
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to rotate refresh token.") from exc

    return build_token_pair(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    payload: RefreshRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db_session),
) -> dict[str, str]:
    _enforce_https_if_required(request)
    await _enforce_rate_limit(request, action="logout", limit=30)

    try:
        decoded = decode_token(payload.refresh_token)
        jti = decoded.get("jti")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.") from exc

    if not isinstance(jti, str) or not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    revoked = await _mark_refresh_token_revoked(session, jti=jti, user_id=current_user.id)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found.")

    try:
        await create_audit_log(
            session=session,
            user_id=current_user.id,
            action="logout",
            resource_type="user",
            resource_id=current_user.id,
            details={"firm_id": current_user.firm_id},
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            firm_id=current_user.firm_id,
        )
    except CrudError:
        # Logout should remain successful even if audit logging fails.
        pass

    return {"status": "logged_out"}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        firm_id=current_user.firm_id,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
