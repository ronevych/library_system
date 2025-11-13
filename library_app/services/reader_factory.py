from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from library_app.models.reader import Reader, ReaderCategory


class ReaderCreator(ABC):
    @abstractmethod
    def create_reader(
        self, full_name: str, address: str, phone: str
    ) -> Reader:
        """Factory method to create a reader instance."""


@dataclass
class BaseReaderCreator(ReaderCreator):
    category: ReaderCategory

    def create_reader(self, full_name: str, address: str, phone: str) -> Reader:
        return Reader(
            full_name=full_name,
            address=address,
            phone=phone,
            category=self.category,
        )


def get_reader_creator(category: ReaderCategory) -> ReaderCreator:
    return BaseReaderCreator(category)


__all__ = ["ReaderCreator", "BaseReaderCreator", "get_reader_creator"]

