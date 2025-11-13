from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from library_app.models import db

if TYPE_CHECKING:
    from library_app.models.reader import Reader


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reader_id: Mapped[int | None] = mapped_column(
        ForeignKey("readers.id"), nullable=True, unique=True
    )

    reader: Mapped["Reader"] = relationship(
        "Reader", back_populates="user", lazy="joined", uselist=False
    )

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


__all__ = ["User", "UserRole"]

