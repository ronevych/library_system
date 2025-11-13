from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import between, select

from library_app.models.payment import Payment
from library_app.repositories import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self) -> None:
        super().__init__(Payment)

    def between_dates(self, start: date, end: date) -> list[Payment]:
        start_dt = datetime.combine(start, datetime.min.time())
        end_dt = datetime.combine(end, datetime.max.time())
        stmt = select(Payment).where(between(Payment.paid_date, start_dt, end_dt))
        return list(self.filter(stmt))


__all__ = ["PaymentRepository"]

