"""
Authentication service for FiscIA Pro.
Password hashing (bcrypt), JWT generation/verification, token blacklisting.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from fiscia.models_db import TokenBlacklist

# --- Password hashing (bcrypt direct, work factor 12) ---

BCRYPT_ROUNDS = 12


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# --- JWT configuration ---

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fiscia-dev-secret-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# --- Role hierarchy ---

ROLES = {"admin": 3, "fiscaliste": 2, "client": 1}


def role_level(role: str) -> int:
    return ROLES.get(role, 0)


def has_role(user_role: str, required_role: str) -> bool:
    """Check if user_role meets or exceeds required_role in the hierarchy."""
    return role_level(user_role) >= role_level(required_role)


# --- Token creation ---

def create_access_token(user_id: str, email: str, role: str, firm_id: Optional[str] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "firm_id": firm_id,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --- Token verification ---

def decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# --- Token blacklisting ---

def blacklist_entry(jti: str, user_id: str, expires_at: datetime) -> TokenBlacklist:
    """Create a TokenBlacklist ORM object (caller must persist it)."""
    return TokenBlacklist(jti=jti, user_id=user_id, expires_at=expires_at)
