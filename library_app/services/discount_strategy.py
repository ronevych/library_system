from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from library_app.models.reader import ReaderCategory


class DiscountStrategy(ABC):
    @abstractmethod
    def get_discount(self) -> float:
        """Return discount factor (0.0 - 1.0)."""


class RegularDiscount(DiscountStrategy):
    def get_discount(self) -> float:
        return 0.0


class PrivilegedDiscount(DiscountStrategy):
    def get_discount(self) -> float:
        return 0.1


class VipDiscount(DiscountStrategy):
    def get_discount(self) -> float:
        return 0.2


@dataclass
class DiscountContext:
    strategy: DiscountStrategy

    def calculate(self, base_amount: float) -> float:
        discount = self.strategy.get_discount()
        return base_amount * (1 - discount)


def strategy_for_category(category: ReaderCategory) -> DiscountStrategy:
    if category == ReaderCategory.PRIVILEGED:
        return PrivilegedDiscount()
    if category == ReaderCategory.VIP:
        return VipDiscount()
    return RegularDiscount()


__all__ = [
    "DiscountStrategy",
    "RegularDiscount",
    "PrivilegedDiscount",
    "VipDiscount",
    "DiscountContext",
    "strategy_for_category",
]

