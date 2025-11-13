from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from library_app.models import db


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[str] = mapped_column(String(128), nullable=False)
    collateral_value: Mapped[float] = mapped_column(Float, nullable=False)
    daily_rent_price: Mapped[float] = mapped_column(Float, nullable=False)
    available_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    rentals: Mapped[list["Rental"]] = relationship(
        "Rental", back_populates="book", cascade="all, delete-orphan"
    )

    def decrease_stock(self) -> None:
        if self.available_copies <= 0:
            raise ValueError("No copies available for rent")
        self.available_copies -= 1

    def increase_stock(self) -> None:
        self.available_copies += 1


__all__ = ["Book"]

