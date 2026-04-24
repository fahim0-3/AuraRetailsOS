# ============================================================
# Subsystem: Inventory  Pattern: Composite  Role: Composite node — bundle of items
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING
from inventory.i_inventory_item import IInventoryItem
from inventory.kiosk_compatibility import kiosk_matches, normalize_kiosk_tags

if TYPE_CHECKING:
    pass


# PATTERN: Composite (Composite node)
class ProductBundle(IInventoryItem):
    def __init__(self, item_id: str, name: str, compatible_kiosks: list[str] | None = None) -> None:
        self._id = item_id
        self._name = name
        self._children: list[IInventoryItem] = []
        self._compatible_kiosks = sorted(normalize_kiosk_tags(compatible_kiosks or []))

    @property
    def item_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return sum(child.price for child in self._children)

    @property
    def compatible_kiosks(self) -> tuple[str, ...]:
        if self._compatible_kiosks:
            return tuple(self._compatible_kiosks)
        # If not explicitly set, aggregate from children
        all_kiosks = set()
        for child in self._children:
            child_kiosks = getattr(child, 'compatible_kiosks', ())
            if not child_kiosks:
                return ()  # If any child is compatible with all, bundle is compatible with all
            all_kiosks.update(child_kiosks)
        return tuple(sorted(all_kiosks))

    # Backward-compatible alias for older typo'd callers.
    @property
    def compatible_kikosks(self) -> tuple[str, ...]:
        return self.compatible_kiosks

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

    def is_compatible_with_kiosk(self, kiosk_type: str) -> bool:
        """Check if bundle is compatible with given kiosk type"""
        # Check explicit setting first
        if self._compatible_kiosks:
            return kiosk_matches(self._compatible_kiosks, kiosk_type)
        # If no explicit setting, check if all children are compatible
        for child in self._children:
            if hasattr(child, 'is_compatible_with_kiosk'):
                if not child.is_compatible_with_kiosk(kiosk_type):
                    return False
            else:
                return True  # If child has no compatibility check, assume compatible
        return True

    def is_bundle(self) -> bool:
        return True

    def display(self, depth: int = 0) -> None:
        indent = "  " * depth
        avail = self.get_available_stock()
        status = "AVAILABLE" if self.is_available() else "UNAVAILABLE"
        kiosks = ",".join(self.compatible_kiosks) if self.compatible_kiosks else "all"
        print(f"{indent}[BUNDLE] {self._name} ({self._id}) — ${self.price:.2f} — stock: {avail} [{status}] [kiosks:{kiosks}]")
        for child in self._children:
            child.display(depth + 1)
