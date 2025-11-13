from __future__ import annotations

from library_app.repositories.book_repository import BookRepository
from library_app.repositories.notification_repository import NotificationRepository
from library_app.repositories.payment_repository import PaymentRepository
from library_app.repositories.reader_repository import ReaderRepository
from library_app.repositories.rental_repository import RentalRepository
from library_app.repositories.user_repository import UserRepository

book_repository = BookRepository()
reader_repository = ReaderRepository()
rental_repository = RentalRepository()
payment_repository = PaymentRepository()
notification_repository = NotificationRepository()
user_repository = UserRepository()

__all__ = [
    "book_repository",
    "reader_repository",
    "rental_repository",
    "payment_repository",
    "notification_repository",
    "user_repository",
]

