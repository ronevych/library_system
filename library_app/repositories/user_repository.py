from __future__ import annotations

from sqlalchemy import func, select

from library_app.models import db
from library_app.models.user import User, UserRole
from library_app.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = self.filter(stmt)
        return result[0] if result else None

    def has_admin(self) -> bool:
        stmt = select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)
        count = db.session.execute(stmt).scalar_one()
        return count > 0


__all__ = ["UserRepository"]

