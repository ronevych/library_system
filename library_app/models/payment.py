from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from library_app.models import db


class Payment(db.Model):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rental_id: Mapped[int] = mapped_column(ForeignKey("rentals.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    paid_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rental: Mapped["Rental"] = relationship("Rental", back_populates="payments")


__all__ = ["Payment"]

