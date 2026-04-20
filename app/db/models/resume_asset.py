from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResumeAsset(Base):
    __tablename__ = "resume_assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    parsed_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
