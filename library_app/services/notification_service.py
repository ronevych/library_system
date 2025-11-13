from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, ClassVar

from library_app.models.notification import Notification
from library_app.models.rental import Rental
from library_app.repositories.notification_repository import NotificationRepository
from library_app.services import notification_repository


class NotificationObserver(ABC):
    @abstractmethod
    def update(self, event: str, payload: dict[str, Any]) -> None:
        """React on notification events."""


class OverdueRentalObserver(NotificationObserver):
    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    def update(self, event: str, payload: dict[str, Any]) -> None:
        if event != "rental_overdue":
            return
        rental: Rental = payload["rental"]
        message = (
            f"Читач {rental.reader.full_name}: книга '{rental.book.title}' прострочена. "
            f"Дата повернення: {rental.due_date:%d.%m.%Y}."
        )
        notification = Notification(reader_id=rental.reader_id, message=message)
        self.repo.add(notification)


class NotificationService:
    _observers: ClassVar[list[NotificationObserver]] = []
    _repo: ClassVar[NotificationRepository] = notification_repository

    @classmethod
    def bootstrap(cls) -> None:
        if not cls._observers:
            cls.register_observer(OverdueRentalObserver(cls._repo))

    @classmethod
    def register_observer(cls, observer: NotificationObserver) -> None:
        cls._observers.append(observer)

    @classmethod
    def notify_overdue(cls, rental: Rental) -> None:
        payload = {"rental": rental, "today": date.today()}
        cls._dispatch("rental_overdue", payload)

    @classmethod
    def _dispatch(cls, event: str, payload: dict[str, Any]) -> None:
        for observer in cls._observers:
            observer.update(event, payload)


__all__ = [
    "NotificationObserver",
    "OverdueRentalObserver",
    "NotificationService",
]

