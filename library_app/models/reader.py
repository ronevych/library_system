from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from library_app.models import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from library_app.models.user import User


class ReaderCategory(StrEnum):
    REGULAR = "regular"
    PRIVILEGED = "privileged"
    VIP = "vip"


class Reader(db.Model):
    __tablename__ = "readers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[ReaderCategory] = mapped_column(
        Enum(ReaderCategory), default=ReaderCategory.REGULAR, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rentals: Mapped[list["Rental"]] = relationship(
        "Rental", back_populates="reader", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="reader", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship("User", back_populates="reader", uselist=False)

    def __repr__(self) -> str:
        return f"<Reader {self.full_name} ({self.category})>"


__all__ = ["Reader", "ReaderCategory"]

