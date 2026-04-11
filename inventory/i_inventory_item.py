# ============================================================
# Subsystem: Inventory  Pattern: Composite  Role: Component interface for products and bundles
# ============================================================

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# PATTERN: Composite (Component interface)
class IInventoryItem(ABC):
    @property
    @abstractmethod
    def item_id(self) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def price(self) -> float: ...

    @abstractmethod
    def get_available_stock(self) -> int: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def display(self, depth: int = 0) -> None: ...

    @abstractmethod
    def is_bundle(self) -> bool: ...
