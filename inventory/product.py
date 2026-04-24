# ============================================================
# Subsystem: Inventory  Pattern: Composite  Role: Leaf node — individual product
# ============================================================

from __future__ import annotations
from inventory.i_inventory_item import IInventoryItem
from inventory.kiosk_compatibility import kiosk_matches, normalize_kiosk_tags, normalize_module_tags


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
        compatible_kiosks: list[str] | None = None,
    ) -> None:
        self._id = item_id
        self._name = name
        self._price = price
        self._total_stock = total_stock
        self._reserved_stock = reserved_stock
        self._hardware_available = hardware_available
        self._required_modules = sorted(normalize_module_tags(required_modules or []))
        self._essential_item = essential_item
        self._compatible_kiosks = sorted(normalize_kiosk_tags(compatible_kiosks or []))

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

    @property
    def compatible_kiosks(self) -> tuple[str, ...]:
        return tuple(self._compatible_kiosks)

    # Backward-compatible alias for older typo'd callers.
    @property
    def compatible_kikosks(self) -> tuple[str, ...]:
        return self.compatible_kiosks

    def get_available_stock(self) -> int:
        return self._total_stock - self._reserved_stock

    def is_available(self) -> bool:
        return self.get_available_stock() > 0 and self._hardware_available

    def is_compatible_with_kiosk(self, kiosk_type: str) -> bool:
        """Check if product is compatible with given kiosk type"""
        return kiosk_matches(self._compatible_kiosks, kiosk_type)

    def set_hardware_available(self, val: bool) -> None:
        self._hardware_available = val

    def is_bundle(self) -> bool:
        return False

    def display(self, depth: int = 0) -> None:
        indent = "  " * depth
        avail = self.get_available_stock()
        hw_status = "OK" if self._hardware_available else "FAULT"
        modules = ",".join(self._required_modules) if self._required_modules else "none"
        kiosks = ",".join(self._compatible_kiosks) if self._compatible_kiosks else "all"
        essential = " ESSENTIAL" if self._essential_item else ""
        print(
            f"{indent}[PRODUCT] {self._name} ({self._id}) — ${self._price:.2f} — stock: {avail} "
            f"[{hw_status}] [requires:{modules}] [kiosks:{kiosks}]{essential}"
        )

    def reserve(self, qty: int) -> None:
        self._reserved_stock += qty

    def release(self, qty: int) -> None:
        self._reserved_stock = max(0, self._reserved_stock - qty)

    def deduct(self, qty: int) -> None:
        self._total_stock = max(0, self._total_stock - qty)

    def restock(self, qty: int) -> None:
        self._total_stock += qty
