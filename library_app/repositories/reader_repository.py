from __future__ import annotations

from sqlalchemy import select

from library_app.models.reader import Reader, ReaderCategory
from library_app.repositories import BaseRepository


class ReaderRepository(BaseRepository[Reader]):
    def __init__(self) -> None:
        super().__init__(Reader)

    def by_category(self, category: ReaderCategory) -> list[Reader]:
        stmt = select(Reader).where(Reader.category == category)
        return list(self.filter(stmt))


__all__ = ["ReaderRepository"]

