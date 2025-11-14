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
        today: date = payload.get("today", date.today())
        days_overdue = (today - rental.due_date).days
        
        # Тільки для прострочених (більше 0 днів)
        if days_overdue > 0:
            message = (
                f"Книга '{rental.book.title}' прострочена на {days_overdue} дн{'ів' if days_overdue > 1 else 'я'}⚠️ "
                f"Дата повернення: {rental.due_date:%d.%m.%Y}."
            )
            notification = Notification(reader_id=rental.reader_id, message=message)
            self.repo.add(notification)


class DueDateRentalObserver(NotificationObserver):
    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    def update(self, event: str, payload: dict[str, Any]) -> None:
        if event != "rental_due_today":
            return
        rental: Rental = payload["rental"]
        message = f"Сьогодні останній день оренди⚠️ Книга '{rental.book.title}' має бути повернена сьогодні ({rental.due_date:%d.%m.%Y})"
        notification = Notification(reader_id=rental.reader_id, message=message)
        self.repo.add(notification)


class NotificationService:
    _observers: ClassVar[list[NotificationObserver]] = []
    _repo: ClassVar[NotificationRepository] = notification_repository

    @classmethod
    def bootstrap(cls) -> None:
        if not cls._observers:
            cls.register_observer(OverdueRentalObserver(cls._repo))
            cls.register_observer(DueDateRentalObserver(cls._repo))

    @classmethod
    def register_observer(cls, observer: NotificationObserver) -> None:
        cls._observers.append(observer)

    @classmethod
    def notify_overdue(cls, rental: Rental) -> None:
        payload = {"rental": rental, "today": date.today()}
        cls._dispatch("rental_overdue", payload)

    @classmethod
    def notify_due_today(cls, rental: Rental) -> None:
        payload = {"rental": rental, "today": date.today()}
        cls._dispatch("rental_due_today", payload)

    @classmethod
    def check_all_rentals(cls) -> None:
        """Перевіряє всі активні оренди та генерує сповіщення для прострочених та тих, що мають бути повернені сьогодні.
        Генерує сповіщення щодня для прострочених оренд."""
        from library_app.services import rental_repository
        
        today = date.today()
        active_rentals = rental_repository.active_rentals()
        
        for rental in active_rentals:
            if rental.return_date is not None:
                continue  # Пропускаємо вже повернуті
            
            days_diff = (today - rental.due_date).days
            
            # Якщо сьогодні день повернення або прострочка
            if days_diff >= 0:
                # Перевіряємо, чи вже є сповіщення за сьогодні для цієї оренди
                existing_notifications = cls._repo.get_by_reader_and_date(rental.reader_id, today)
                rental_notified_today = any(
                    f"'{rental.book.title}'" in notif.message for notif in existing_notifications
                )
                
                if not rental_notified_today:
                    if days_diff == 0:
                        cls.notify_due_today(rental)
                    else:
                        # Для прострочених - генеруємо сповіщення з кількістю днів прострочки
                        cls.notify_overdue(rental)

    @classmethod
    def _dispatch(cls, event: str, payload: dict[str, Any]) -> None:
        for observer in cls._observers:
            observer.update(event, payload)


__all__ = [
    "NotificationObserver",
    "OverdueRentalObserver",
    "DueDateRentalObserver",
    "NotificationService",
]

