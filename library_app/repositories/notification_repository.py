from __future__ import annotations

from datetime import date

from sqlalchemy import and_, func, select

from library_app.models.notification import Notification
from library_app.repositories import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self) -> None:
        super().__init__(Notification)

    def unread_for_reader(self, reader_id: int) -> list[Notification]:
        stmt = select(Notification).where(
            Notification.reader_id == reader_id, Notification.is_read.is_(False)
        )
        return list(self.filter(stmt))

    def get_by_reader_and_date(self, reader_id: int, check_date: date) -> list[Notification]:
        """Отримує сповіщення для читача за конкретну дату."""
        stmt = select(Notification).where(
            and_(
                Notification.reader_id == reader_id,
                func.date(Notification.created_at) == check_date
            )
        )
        return list(self.filter(stmt))


__all__ = ["NotificationRepository"]

