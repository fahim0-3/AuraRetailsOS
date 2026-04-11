# ============================================================
# Subsystem: Inventory  Pattern: Composite  Role: Leaf node — individual product
# ============================================================

from __future__ import annotations
from typing import Optional
from inventory.i_inventory_item import IInventoryItem


# PATTERN: Composite (Leaf)
class Product(IInventoryItem):
    def __init__(
        self,
        item_id: str,
        name: str,
        price: float,
        total_stock: int = 0,
        reserved_stock: int = 0,
        hardware_available: bool = True,
    ) -> None:
        self._id = item_id
        self._name = name
        self._price = price
        self._total_stock = total_stock
        self._reserved_stock = reserved_stock
        self._hardware_available = hardware_available

    @property
    def item_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    def get_available_stock(self) -> int:
        return self._total_stock - self._reserved_stock

    def is_available(self) -> bool:
        return self.get_available_stock() > 0 and self._hardware_available

    def set_hardware_available(self, val: bool) -> None:
        self._hardware_available = val

    def is_bundle(self) -> bool:
        return False

    def display(self, depth: int = 0) -> None:
        indent = "  " * depth
        avail = self.get_available_stock()
        hw_status = "OK" if self._hardware_available else "FAULT"
        print(f"{indent}[PRODUCT] {self._name} ({self._id}) — ${self._price:.2f} — stock: {avail} [{hw_status}]")

    def reserve(self, qty: int) -> None:
        self._reserved_stock += qty

    def release(self, qty: int) -> None:
        self._reserved_stock = max(0, self._reserved_stock - qty)

    def deduct(self, qty: int) -> None:
        self._total_stock = max(0, self._total_stock - qty)

    def restock(self, qty: int) -> None:
        self._total_stock += qty
