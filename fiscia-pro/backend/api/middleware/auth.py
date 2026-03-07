"""Authentication dependency stubs (JWT integration point)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from fastapi import Header, HTTPException, status


@dataclass(slots=True)
class AuthUser:
    id: uuid.UUID
    role: str = "user"


async def get_current_user(authorization: str | None = Header(default=None)) -> AuthUser:
    if not authorization:
        # Development fallback: allow anonymous simulation without failing local flow.
        return AuthUser(id=uuid.uuid4(), role="admin")

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    return AuthUser(id=uuid.uuid4(), role="user")

