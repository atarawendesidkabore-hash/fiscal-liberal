from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.auth_models import Role, User, decode_token
from fiscia.dependencies import get_async_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ROLE_HIERARCHY: dict[str, int] = {
    Role.CLIENT.value: 1,
    Role.FISCALISTE.value: 2,
    Role.ADMIN.value: 3,
}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_db_session),
) -> User:
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required.",
        )

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing.",
        )

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
        ) from exc

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    return user


def require_role(min_role: str) -> Callable:
    if min_role not in ROLE_HIERARCHY:
        raise ValueError(f"Unknown role: {min_role}")

    async def _role_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_rank = ROLE_HIERARCHY.get(current_user.role, 0)
        if user_rank < ROLE_HIERARCHY[min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return _role_dependency


def ensure_same_firm(*, current_user: User, resource_firm_id: int | None) -> None:
    if resource_firm_id is None:
        return
    if current_user.firm_id != resource_firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied outside current firm scope.",
        )


def firm_data_isolation(target_firm_id: int) -> Callable:
    async def _firm_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.firm_id != target_firm_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cross-firm access denied.",
            )
        return current_user

    return _firm_dependency