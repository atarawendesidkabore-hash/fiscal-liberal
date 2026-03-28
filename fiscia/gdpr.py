"""
FiscIA Pro — GDPR compliance endpoints.
Data export, right-to-deletion, consent tracking, retention policies.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from fiscia.database_async import get_async_db
from fiscia.dependencies import CurrentUser, get_current_user, require_role
from fiscia.models_db import (
    AuditLog,
    GDPRConsent,
    LiasseCalculation,
    TokenBlacklist,
    User,
)

logger = logging.getLogger("fiscia.gdpr")

router = APIRouter(prefix="/gdpr", tags=["gdpr"])

# Retention policy: calculations older than this (days) can be purged
RETENTION_DAYS = 365 * 3  # 3 years (French accounting obligation minimum)


# --- Schemas ---

class ConsentRequest(BaseModel):
    consent_type: str = Field(..., pattern="^(data_processing|marketing|analytics)$")
    granted: bool


class ConsentResponse(BaseModel):
    id: str
    consent_type: str
    granted: bool
    created_at: Optional[str]
    revoked_at: Optional[str]


class DataExportResponse(BaseModel):
    user: dict
    consents: list
    calculations: list
    audit_logs: list
    exported_at: str


class DeletionResponse(BaseModel):
    deleted: bool
    user_id: str
    calculations_deleted: int
    audit_logs_anonymized: int
    consents_revoked: int
    tokens_purged: int


class RetentionReport(BaseModel):
    total_calculations: int
    expired_calculations: int
    retention_days: int


# --- Consent endpoints ---

@router.post("/consent", response_model=ConsentResponse, status_code=201)
async def grant_consent(
    req: ConsentRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Record or update GDPR consent."""
    # Check if consent of this type already exists
    result = await db.execute(
        select(GDPRConsent).where(
            GDPRConsent.user_id == user.id,
            GDPRConsent.consent_type == req.consent_type,
            GDPRConsent.revoked_at.is_(None),
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        if req.granted == existing.granted:
            return ConsentResponse(
                id=existing.id,
                consent_type=existing.consent_type,
                granted=existing.granted,
                created_at=existing.created_at.isoformat() if existing.created_at else None,
                revoked_at=None,
            )
        # Revoke old, create new
        existing.revoked_at = datetime.now(timezone.utc)

    consent = GDPRConsent(
        user_id=user.id,
        consent_type=req.consent_type,
        granted=req.granted,
    )
    db.add(consent)
    await db.commit()
    await db.refresh(consent)

    logger.info("GDPR consent %s: user=%s type=%s granted=%s",
                "granted" if req.granted else "revoked", user.id, req.consent_type, req.granted)

    return ConsentResponse(
        id=consent.id,
        consent_type=consent.consent_type,
        granted=consent.granted,
        created_at=consent.created_at.isoformat() if consent.created_at else None,
        revoked_at=None,
    )


@router.get("/consent", response_model=List[ConsentResponse])
async def list_consents(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List all active consents for the current user."""
    result = await db.execute(
        select(GDPRConsent).where(
            GDPRConsent.user_id == user.id,
            GDPRConsent.revoked_at.is_(None),
        )
    )
    consents = result.scalars().all()
    return [
        ConsentResponse(
            id=c.id,
            consent_type=c.consent_type,
            granted=c.granted,
            created_at=c.created_at.isoformat() if c.created_at else None,
            revoked_at=None,
        )
        for c in consents
    ]


# --- Data export (Art. 20 GDPR — portability) ---

@router.get("/export", response_model=DataExportResponse)
async def export_data(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Export all personal data for the current user (GDPR Art. 20)."""
    # User profile
    user_result = await db.execute(select(User).where(User.id == user.id))
    user_record = user_result.scalar_one_or_none()
    if not user_record:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve.")

    user_data = {
        "id": user_record.id,
        "email": user_record.email,
        "full_name": user_record.full_name,
        "role": user_record.role,
        "firm_id": user_record.firm_id,
        "created_at": user_record.created_at.isoformat() if user_record.created_at else None,
    }

    # Consents
    consents_result = await db.execute(
        select(GDPRConsent).where(GDPRConsent.user_id == user.id)
    )
    consents = [
        {
            "consent_type": c.consent_type,
            "granted": c.granted,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
        }
        for c in consents_result.scalars().all()
    ]

    # Calculations
    calcs_result = await db.execute(
        select(LiasseCalculation).where(LiasseCalculation.user_id == user.id)
    )
    calculations = [
        {
            "id": c.id,
            "siren": c.siren,
            "exercice_clos": c.exercice_clos,
            "input_data": c.input_data,
            "result_data": c.result_data,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in calcs_result.scalars().all()
    ]

    # Audit logs
    logs_result = await db.execute(
        select(AuditLog).where(AuditLog.user_id == user.id)
    )
    audit_logs = [
        {
            "action": log_entry.action,
            "module": log_entry.module,
            "siren": log_entry.siren,
            "detail": log_entry.detail,
            "created_at": log_entry.created_at.isoformat() if log_entry.created_at else None,
        }
        for log_entry in logs_result.scalars().all()
    ]

    logger.info("GDPR data export: user=%s, calcs=%d, logs=%d", user.id, len(calculations), len(audit_logs))

    return DataExportResponse(
        user=user_data,
        consents=consents,
        calculations=calculations,
        audit_logs=audit_logs,
        exported_at=datetime.now(timezone.utc).isoformat(),
    )


# --- Right to deletion (Art. 17 GDPR — right to erasure) ---

@router.delete("/delete-me", response_model=DeletionResponse)
async def delete_my_data(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Delete all personal data for the current user (GDPR Art. 17).

    This:
    1. Deletes all saved calculations
    2. Anonymizes audit logs (replaces user_id with 'DELETED')
    3. Revokes all consents
    4. Purges all tokens
    5. Deactivates the user account
    """
    user_id = user.id

    # 1. Delete calculations
    calc_result = await db.execute(
        delete(LiasseCalculation).where(LiasseCalculation.user_id == user_id)
    )
    calcs_deleted = calc_result.rowcount

    # 2. Anonymize audit logs (keep for compliance, but strip PII)
    audit_result = await db.execute(
        update(AuditLog)
        .where(AuditLog.user_id == user_id)
        .values(user_id="DELETED", ip_address=None)
    )
    logs_anonymized = audit_result.rowcount

    # 3. Revoke all consents
    now = datetime.now(timezone.utc)
    consent_result = await db.execute(
        update(GDPRConsent)
        .where(GDPRConsent.user_id == user_id, GDPRConsent.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    consents_revoked = consent_result.rowcount

    # 4. Purge tokens
    token_result = await db.execute(
        delete(TokenBlacklist).where(TokenBlacklist.user_id == user_id)
    )
    tokens_purged = token_result.rowcount

    # 5. Deactivate user account and strip PII
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            is_active=False,
            email=f"deleted-{user_id[:8]}@deleted.local",
            full_name=None,
            hashed_password="DELETED",
        )
    )

    await db.commit()

    logger.info(
        "GDPR deletion: user=%s calcs=%d logs=%d consents=%d tokens=%d",
        user_id, calcs_deleted, logs_anonymized, consents_revoked, tokens_purged,
    )

    return DeletionResponse(
        deleted=True,
        user_id=user_id,
        calculations_deleted=calcs_deleted,
        audit_logs_anonymized=logs_anonymized,
        consents_revoked=consents_revoked,
        tokens_purged=tokens_purged,
    )


# --- Data retention policy (admin) ---

@router.get("/retention/report", response_model=RetentionReport)
async def retention_report(
    admin: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """Report on data eligible for retention-based cleanup (admin only)."""
    from sqlalchemy import func

    total_result = await db.execute(select(func.count(LiasseCalculation.id)))
    total = total_result.scalar() or 0

    cutoff = datetime.now(timezone.utc).replace(
        year=datetime.now(timezone.utc).year - (RETENTION_DAYS // 365)
    )
    expired_result = await db.execute(
        select(func.count(LiasseCalculation.id)).where(
            LiasseCalculation.created_at < cutoff
        )
    )
    expired = expired_result.scalar() or 0

    return RetentionReport(
        total_calculations=total,
        expired_calculations=expired,
        retention_days=RETENTION_DAYS,
    )


@router.post("/retention/purge")
async def purge_expired(
    admin: CurrentUser = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_async_db),
):
    """Purge calculations older than retention period (admin only)."""
    cutoff = datetime.now(timezone.utc).replace(
        year=datetime.now(timezone.utc).year - (RETENTION_DAYS // 365)
    )
    result = await db.execute(
        delete(LiasseCalculation).where(LiasseCalculation.created_at < cutoff)
    )
    await db.commit()

    logger.info("GDPR retention purge: %d calculations deleted (cutoff=%s)", result.rowcount, cutoff.isoformat())

    return {"purged": result.rowcount, "cutoff": cutoff.isoformat()}
