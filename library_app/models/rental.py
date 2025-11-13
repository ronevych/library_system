from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from library_app.models import db


class Rental(db.Model):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False)
    rent_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fine_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    book: Mapped["Book"] = relationship("Book", back_populates="rentals")
    reader: Mapped["Reader"] = relationship("Reader", back_populates="rentals")
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="rental", cascade="all, delete-orphan"
    )

    @property
    def is_returned(self) -> bool:
        return self.return_date is not None


__all__ = ["Rental"]

