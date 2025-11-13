from __future__ import annotations

from sqlalchemy import or_, select

from library_app.models.book import Book
from library_app.repositories import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self) -> None:
        super().__init__(Book)

    def find_available(self) -> list[Book]:
        stmt = select(Book).where(Book.available_copies > 0)
        return list(self.filter(stmt))

    def search_available(self, query: str) -> list[Book]:
        pattern = f"%{query.strip()}%"
        stmt = select(Book).where(
            Book.available_copies > 0,
            or_(Book.title.ilike(pattern), Book.author.ilike(pattern), Book.genre.ilike(pattern)),
        )
        return list(self.filter(stmt))


__all__ = ["BookRepository"]

