from __future__ import annotations

from typing import Generic, Iterable, Optional, Type, TypeVar

from sqlalchemy import Select

from library_app.models import db

ModelType = TypeVar("ModelType", bound=db.Model)


class BaseRepository(Generic[ModelType]):
    model_class: Type[ModelType]

    def __init__(self, model_class: Type[ModelType]) -> None:
        self.model_class = model_class

    def get(self, model_id: int) -> Optional[ModelType]:
        return self.model_class.query.get(model_id)

    def all(self) -> Iterable[ModelType]:
        return self.model_class.query.all()

    def add(self, instance: ModelType) -> ModelType:
        db.session.add(instance)
        db.session.commit()
        return instance

    def delete(self, instance: ModelType) -> None:
        db.session.delete(instance)
        db.session.commit()

    def update(self) -> None:
        db.session.commit()

    def filter(self, select_stmt: Select) -> Iterable[ModelType]:
        return db.session.execute(select_stmt).scalars().all()


__all__ = ["BaseRepository"]

