# ============================================================
# Subsystem: Inventory  Pattern: Composite  Role: Composite node — bundle of items
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING
from inventory.i_inventory_item import IInventoryItem

if TYPE_CHECKING:
    pass


# PATTERN: Composite (Composite node)
class ProductBundle(IInventoryItem):
    def __init__(self, item_id: str, name: str) -> None:
        self._id = item_id
        self._name = name
        self._children: list[IInventoryItem] = []

    @property
    def item_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return sum(child.price for child in self._children)

    def add_item(self, item: IInventoryItem) -> None:
        self._children.append(item)

    def remove_item(self, item_id: str) -> None:
        self._children = [c for c in self._children if c.item_id != item_id]

    def get_available_stock(self) -> int:
        if not self._children:
            return 0
        return min(child.get_available_stock() for child in self._children)

    def is_available(self) -> bool:
        return all(child.is_available() for child in self._children)

    def is_bundle(self) -> bool:
        return True

    def display(self, depth: int = 0) -> None:
        indent = "  " * depth
        avail = self.get_available_stock()
        status = "AVAILABLE" if self.is_available() else "UNAVAILABLE"
        print(f"{indent}[BUNDLE] {self._name} ({self._id}) — ${self.price:.2f} — stock: {avail} [{status}]")
        for child in self._children:
            child.display(depth + 1)
