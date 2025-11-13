from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from library_app.models import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False)
    message: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    reader: Mapped["Reader"] = relationship("Reader", back_populates="notifications")

    def mark_read(self) -> None:
        self.is_read = True


__all__ = ["Notification"]

