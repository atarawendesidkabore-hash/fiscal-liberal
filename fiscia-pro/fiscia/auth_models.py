from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

import bcrypt
import jwt
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fiscia.models_db import Base

BCRYPT_ROUNDS = 12
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_ALGORITHM = "HS256"
DEFAULT_JWT_SECRET = "change-me-in-production-32-chars-min"


class Role(str, Enum):
    ADMIN = "admin"
    FISCALISTE = "fiscaliste"
    CLIENT = "client"


class Firm(Base):
    __tablename__ = "firms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    plan_type: Mapped[str] = mapped_column(String(32), nullable=False, default="starter", server_default="starter")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    users: Mapped[list["User"]] = relationship("User", back_populates="firm", cascade="all, delete-orphan")
    calculations: Mapped[list["LiasseCalculation"]] = relationship("LiasseCalculation", back_populates="firm")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="firm")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default=Role.CLIENT.value, server_default=Role.CLIENT.value)
    firm_id: Mapped[int] = mapped_column(ForeignKey("firms.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    firm: Mapped[Firm] = relationship("Firm", back_populates="users")
    calculations: Mapped[list["LiasseCalculation"]] = relationship("LiasseCalculation", back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")


class _FlexibleSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class RegisterRequest(_FlexibleSchema):
    firm_name: str = Field(..., min_length=2, max_length=255)
    plan_type: str = Field(default="starter", min_length=2, max_length=32)
    email: str = Field(..., min_length=6, max_length=255)
    password: str = Field(..., min_length=12, max_length=256)


class LoginRequest(_FlexibleSchema):
    email: str = Field(..., min_length=6, max_length=255)
    password: str = Field(..., min_length=1, max_length=256)


class RefreshRequest(_FlexibleSchema):
    refresh_token: str = Field(..., min_length=16)


class TokenPair(_FlexibleSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_in: int
    refresh_expires_in: int


class UserOut(_FlexibleSchema):
    id: int
    email: str
    role: str
    firm_id: int
    is_active: bool
    created_at: datetime


class AuthResponse(_FlexibleSchema):
    user: UserOut
    tokens: TokenPair


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY", DEFAULT_JWT_SECRET)
    app_env = os.getenv("APP_ENV", os.getenv("ENV", "development")).lower()
    if app_env in {"prod", "production"} and secret == DEFAULT_JWT_SECRET:
        raise RuntimeError("JWT secret must be set in production.")
    return secret


def validate_password_policy(password: str) -> None:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")
    if re.search(r"[A-Z]", password) is None:
        raise ValueError("Password must include at least one uppercase letter.")
    if re.search(r"[a-z]", password) is None:
        raise ValueError("Password must include at least one lowercase letter.")
    if re.search(r"\d", password) is None:
        raise ValueError("Password must include at least one digit.")
    if re.search(r"[^A-Za-z0-9]", password) is None:
        raise ValueError("Password must include at least one special character.")


def hash_password(password: str) -> str:
    validate_password_policy(password)
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def _create_token(*, claims: dict[str, Any], token_type: str, expires_delta: timedelta) -> tuple[str, str, datetime]:
    now = _now_utc()
    expires_at = now + expires_delta
    jti = str(uuid4())
    payload = {
        **claims,
        "type": token_type,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    token = jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)
    return token, jti, expires_at


def create_access_token(*, user_id: int, email: str, role: str, firm_id: int) -> tuple[str, str, datetime]:
    return _create_token(
        claims={"sub": str(user_id), "email": email, "role": role, "firm_id": firm_id},
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(*, user_id: int, email: str, role: str, firm_id: int) -> tuple[str, str, datetime]:
    return _create_token(
        claims={"sub": str(user_id), "email": email, "role": role, "firm_id": firm_id},
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid or expired token.") from exc
    return payload


def build_token_pair(*, access_token: str, refresh_token: str) -> TokenPair:
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        access_expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
