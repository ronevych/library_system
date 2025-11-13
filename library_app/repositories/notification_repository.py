from __future__ import annotations

from sqlalchemy import select

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


__all__ = ["NotificationRepository"]

