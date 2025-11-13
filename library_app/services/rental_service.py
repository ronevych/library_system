from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from library_app.models.payment import Payment
from library_app.models.rental import Rental
from library_app.services import (
    book_repository,
    payment_repository,
    reader_repository,
    rental_repository,
)
from library_app.services.discount_strategy import DiscountContext, strategy_for_category
from library_app.services.notification_service import NotificationService


class RentalError(RuntimeError):
    pass


@dataclass
class RentalSummary:
    rental: Rental
    amount_due: float
    discount_applied: float
    fine_amount: float
    days_rented: int


class RentalService:
    def rent_book(self, book_id: int, reader_id: int, days: int) -> Rental:
        book = book_repository.get(book_id)
        reader = reader_repository.get(reader_id)

        if book is None or reader is None:
            raise RentalError("Book or reader not found")

        if book.available_copies <= 0:
            raise RentalError("No available copies")

        rent_date = date.today()
        due_date = rent_date + timedelta(days=days)

        book.decrease_stock()
        rental = Rental(book_id=book.id, reader_id=reader.id, rent_date=rent_date, due_date=due_date)
        rental_repository.add(rental)
        book_repository.update()
        return rental

    def return_book(self, rental_id: int, return_date: date | None = None) -> RentalSummary:
        rental = rental_repository.get(rental_id)
        if rental is None:
            raise RentalError("Rental not found")
        if rental.is_returned:
            raise RentalError("Rental already closed")

        return_dt = return_date or date.today()
        rental.return_date = return_dt

        book = rental.book
        book.increase_stock()

        days_rented = max((return_dt - rental.rent_date).days, 1)
        base_amount = book.daily_rent_price * days_rented

        reader = rental.reader
        discount_strategy = strategy_for_category(reader.category)
        discount_context = DiscountContext(discount_strategy)
        discounted_amount = discount_context.calculate(base_amount)
        discount_value = base_amount - discounted_amount

        fine = 0.0
        if return_dt > rental.due_date:
            overdue_days = (return_dt - rental.due_date).days
            fine = overdue_days * (book.daily_rent_price * 0.5)
        rental.fine_amount = fine

        total = discounted_amount + fine

        payment = Payment(rental_id=rental.id, total_amount=total)
        payment_repository.add(payment)
        rental_repository.update()
        book_repository.update()

        summary = RentalSummary(
            rental=rental,
            amount_due=total,
            discount_applied=discount_value,
            fine_amount=fine,
            days_rented=days_rented,
        )
        return summary

    def check_overdue_rentals(self) -> None:
        for rental in rental_repository.overdue_rentals():
            NotificationService.notify_overdue(rental)


rental_service = RentalService()

__all__ = ["RentalService", "RentalSummary", "RentalError", "rental_service"]

