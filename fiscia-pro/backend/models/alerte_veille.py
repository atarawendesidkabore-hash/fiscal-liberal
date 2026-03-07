"""Tax watch alert model."""

from __future__ import annotations

import uuid

from sqlalchemy import Date, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utcnow


class AlerteVeille(Base):
    __tablename__ = "alertes_veille"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    urgence: Mapped[str] = mapped_column(String(16), nullable=False, default="A_SURVEILLER")
    titre: Mapped[str] = mapped_column(String(255), nullable=False)
    resume: Mapped[str] = mapped_column(Text, nullable=False)
    date_entree_vigueur: Mapped[Date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    action_recommandee: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow)

