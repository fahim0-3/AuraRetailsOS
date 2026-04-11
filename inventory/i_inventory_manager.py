# ============================================================
# Subsystem: Inventory  Pattern: Proxy  Role: Abstract interface for inventory managers
# ============================================================

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from inventory.i_inventory_item import IInventoryItem


class IInventoryManager(ABC):
    @abstractmethod
    def get_item(self, item_id: str) -> Optional[IInventoryItem]: ...

    @abstractmethod
    def update_stock(self, item_id: str, delta: int) -> bool: ...

    @abstractmethod
    def list_all(self) -> None: ...

    @abstractmethod
    def add_item(self, item: IInventoryItem) -> bool: ...

    @abstractmethod
    def restock(self, item_id: str, qty: int) -> bool: ...

    @abstractmethod
    def deduct_total_stock(self, item_id: str, qty: int) -> bool: ...

    @abstractmethod
    def finalize_purchase(self, item_id: str, qty: int) -> bool: ...
