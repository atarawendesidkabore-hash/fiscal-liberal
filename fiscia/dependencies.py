"""
FastAPI dependencies for authentication and RBAC.
"""
import logging
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.auth import decode_token, has_role
from fiscia.database_async import get_async_db
from fiscia.models_db import TokenBlacklist, User

logger = logging.getLogger("fiscia.dependencies")

bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Lightweight container for the authenticated user context."""
    __slots__ = ("id", "email", "role", "firm_id")

    def __init__(self, user_id: str, email: str, role: str, firm_id: Optional[str]):
        self.id = user_id
        self.email = email
        self.role = role
        self.firm_id = firm_id


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> CurrentUser:
    """Extract and validate the JWT from the Authorization header."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification requis.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expire.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide.")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Type de token invalide.")

    # Check blacklist
    jti = payload.get("jti")
    if jti:
        result = await db.execute(select(TokenBlacklist).where(TokenBlacklist.jti == jti))
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoque.")

    # Verify user still exists and is active
    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur inactif ou supprime.")

    return CurrentUser(
        user_id=user.id,
        email=user.email,
        role=user.role,
        firm_id=user.firm_id,
    )


def require_role(required: str):
    """Dependency factory: reject if user's role is below `required`."""
    async def _check(user: CurrentUser = Depends(get_current_user)):
        if not has_role(user.role, required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required}' ou superieur requis.",
            )
        return user
    return _check


def firm_scoped(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dependency that ensures the user belongs to a firm (multi-tenant guard)."""
    if user.firm_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucun cabinet associe a cet utilisateur.",
        )
    return user
