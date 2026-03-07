"""Authentication endpoints scaffold."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginInput(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(payload: LoginInput) -> dict:
    return {"access_token": "dev-token", "token_type": "bearer", "email": payload.email}
