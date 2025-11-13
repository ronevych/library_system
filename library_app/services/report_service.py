from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from library_app.services import book_repository, payment_repository, rental_repository


@dataclass
class BookInventoryItem:
    title: str
    author: str
    available_copies: int
    lent_out: int


@dataclass
class OverdueRentalItem:
    reader: str
    book: str
    due_date: date
    days_overdue: int


@dataclass
class FinancialSummary:
    total_income: float
    payments_count: int


class ReportService:
    def book_inventory_report(self) -> list[BookInventoryItem]:
        items: list[BookInventoryItem] = []
        for book in book_repository.all():
            lent_out = sum(1 for rent in book.rentals if not rent.is_returned)
            items.append(
                BookInventoryItem(
                    title=book.title,
                    author=book.author,
                    available_copies=book.available_copies,
                    lent_out=lent_out,
                )
            )
        return items

    def overdue_report(self) -> list[OverdueRentalItem]:
        items: list[OverdueRentalItem] = []
        today = date.today()
        for rental in rental_repository.overdue_rentals(today):
            days_overdue = (today - rental.due_date).days
            items.append(
                OverdueRentalItem(
                    reader=rental.reader.full_name,
                    book=rental.book.title,
                    due_date=rental.due_date,
                    days_overdue=days_overdue,
                )
            )
        return items

    def financial_report(self, start: date, end: date) -> FinancialSummary:
        payments = payment_repository.between_dates(start, end)
        total = sum(payment.total_amount for payment in payments)
        return FinancialSummary(total_income=total, payments_count=len(payments))


report_service = ReportService()

__all__ = [
    "ReportService",
    "BookInventoryItem",
    "OverdueRentalItem",
    "FinancialSummary",
    "report_service",
]

