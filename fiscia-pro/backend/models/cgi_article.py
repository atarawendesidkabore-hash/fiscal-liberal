"""CGI article corpus used for semantic retrieval."""

from __future__ import annotations

import uuid

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utcnow


class CGIArticle(Base):
    __tablename__ = "cgi_articles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    titre: Mapped[str] = mapped_column(String(255), nullable=False)
    contenu: Mapped[str] = mapped_column(Text, nullable=False)
    version_label: Mapped[str] = mapped_column(String(64), nullable=False, default="LFI 2024")
    bofip_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    embedding: Mapped[list[float]] = mapped_column(JSONB, default=list)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow)

