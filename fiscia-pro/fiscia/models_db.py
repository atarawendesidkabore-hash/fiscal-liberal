from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LiasseCalculation(Base):
    __tablename__ = "liasse_calculations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    firm_id: Mapped[int | None] = mapped_column(ForeignKey("firms.id", ondelete="SET NULL"), nullable=True, index=True)
    siren: Mapped[str] = mapped_column(String(9), nullable=False, index=True)
    exercice_clos: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    user: Mapped["User | None"] = relationship("User", back_populates="calculations")
    firm: Mapped["Firm | None"] = relationship("Firm", back_populates="calculations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    firm_id: Mapped[int | None] = mapped_column(ForeignKey("firms.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )

    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")
    firm: Mapped["Firm | None"] = relationship("Firm", back_populates="audit_logs")


Index("ix_liasse_calculations_user_created", LiasseCalculation.user_id, LiasseCalculation.created_at.desc())
Index("ix_liasse_calculations_siren_exercice", LiasseCalculation.siren, LiasseCalculation.exercice_clos)

# Register auth ORM models on the same metadata.
import fiscia.auth_models  # noqa: E402,F401
import fiscia.billing_models  # noqa: E402,F401
