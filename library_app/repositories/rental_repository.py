from __future__ import annotations

from datetime import date

from sqlalchemy import and_, select

from library_app.models.rental import Rental
from library_app.repositories import BaseRepository


class RentalRepository(BaseRepository[Rental]):
    def __init__(self) -> None:
        super().__init__(Rental)

    def active_rentals(self) -> list[Rental]:
        stmt = select(Rental).where(Rental.return_date.is_(None))
        return list(self.filter(stmt))

    def overdue_rentals(self, reference_date: date | None = None) -> list[Rental]:
        ref_date = reference_date or date.today()
        stmt = select(Rental).where(
            and_(Rental.return_date.is_(None), Rental.due_date < ref_date)
        )
        return list(self.filter(stmt))

    def for_reader(self, reader_id: int, active_only: bool = False) -> list[Rental]:
        stmt = select(Rental).where(Rental.reader_id == reader_id)
        if active_only:
            stmt = stmt.where(Rental.return_date.is_(None))
        return list(self.filter(stmt))


__all__ = ["RentalRepository"]

