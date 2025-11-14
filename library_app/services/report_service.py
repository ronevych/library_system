from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

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


@dataclass
class ReaderRentalInfo:
    reader_id: int
    reader_name: str
    reader_category: str
    total_rentals: int
    active_rentals: int
    book_rentals: list[dict[str, Any]]  # [{book_title, rental_count}]


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

    def readers_rental_report(self) -> list[ReaderRentalInfo]:
        from library_app.services import reader_repository
        from collections import Counter
        
        readers_info: list[ReaderRentalInfo] = []
        
        for reader in reader_repository.all():
            rentals = rental_repository.for_reader(reader.id, active_only=False)
            active_rentals = rental_repository.for_reader(reader.id, active_only=True)
            
            # Підрахунок кількості оренд по кожній книзі
            book_counter = Counter()
            for rental in rentals:
                book_counter[rental.book.title] += 1
            
            book_rentals = [
                {"book_title": title, "rental_count": count}
                for title, count in book_counter.items()
            ]
            
            readers_info.append(
                ReaderRentalInfo(
                    reader_id=reader.id,
                    reader_name=reader.full_name,
                    reader_category=reader.category.value,
                    total_rentals=len(rentals),
                    active_rentals=len(active_rentals),
                    book_rentals=book_rentals,
                )
            )
        
        return readers_info


report_service = ReportService()

__all__ = [
    "ReportService",
    "BookInventoryItem",
    "OverdueRentalItem",
    "FinancialSummary",
    "ReaderRentalInfo",
    "report_service",
]

