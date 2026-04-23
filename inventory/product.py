# ============================================================
# Subsystem: Inventory  Pattern: Composite  Role: Leaf node — individual product
# ============================================================

from __future__ import annotations
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
        required_modules: list[str] | None = None,
        essential_item: bool = False,
    ) -> None:
        self._id = item_id
        self._name = name
        self._price = price
        self._total_stock = total_stock
        self._reserved_stock = reserved_stock
        self._hardware_available = hardware_available
        self._required_modules = sorted(
            {
                module.strip().lower()
                for module in (required_modules or [])
                if module.strip()
            }
        )
        self._essential_item = essential_item

    @property
    def item_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def required_modules(self) -> tuple[str, ...]:
        return tuple(self._required_modules)

    @property
    def is_essential_item(self) -> bool:
        return self._essential_item

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
        modules = ",".join(self._required_modules) if self._required_modules else "none"
        essential = " ESSENTIAL" if self._essential_item else ""
        print(
            f"{indent}[PRODUCT] {self._name} ({self._id}) — ${self._price:.2f} — stock: {avail} "
            f"[{hw_status}] [requires:{modules}]{essential}"
        )

    def reserve(self, qty: int) -> None:
        self._reserved_stock += qty

    def release(self, qty: int) -> None:
        self._reserved_stock = max(0, self._reserved_stock - qty)

    def deduct(self, qty: int) -> None:
        self._total_stock = max(0, self._total_stock - qty)

    def restock(self, qty: int) -> None:
        self._total_stock += qty
