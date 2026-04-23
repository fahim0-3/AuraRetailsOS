# ============================================================
# Subsystem: Inventory  Pattern: Proxy  Role: Authorization and logging wrapper
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

from core.central_registry import CentralRegistry
from inventory.i_inventory_manager import IInventoryManager
from inventory.inventory_manager import InventoryManager

if TYPE_CHECKING:
    from inventory.i_inventory_item import IInventoryItem


class InventoryProxy(IInventoryManager):
    def __init__(self, role: str) -> None:
        self._real = InventoryManager()
        self._role = role  # "admin", "user", "technician"

    def get_item(self, item_id: str) -> Optional[IInventoryItem]:
        CentralRegistry.get_instance().log_event(
            f"[InventoryProxy] get_item({item_id}) by {self._role}"
        )
        return self._real.get_item(item_id)

    def update_stock(self, item_id: str, delta: int) -> bool:
        # Reservations (negative delta) are allowed for all roles
        # Restocking (positive delta) requires admin or technician
        if delta > 0 and self._role not in ("admin", "technician"):
            CentralRegistry.get_instance().log_event(
                f"[InventoryProxy] UNAUTHORIZED update_stock({item_id}, {delta}) by {self._role}"
            )
            return False
        return self._real.update_stock(item_id, delta)

    def add_item(self, item: IInventoryItem) -> bool:
        if self._role != "admin":
            CentralRegistry.get_instance().log_event(
                f"[InventoryProxy] UNAUTHORIZED add_item({item.item_id}) by {self._role}"
            )
            return False
        return self._real.add_item(item)

    def list_all(self) -> None:
        self._real.list_all()

    def restock(self, item_id: str, qty: int) -> bool:
        if self._role not in ("admin", "technician"):
            CentralRegistry.get_instance().log_event(
                f"[InventoryProxy] UNAUTHORIZED restock({item_id}) by {self._role}"
            )
            return False
        return self._real.restock(item_id, qty)
    def deduct_total_stock(self, item_id: str, qty: int) -> bool:
        if self._role not in ("admin", "technician"):
            CentralRegistry.get_instance().log_event(
                f"[InventoryProxy] UNAUTHORIZED deduct_total_stock({item_id}) by {self._role}"
            )
            return False
        return self._real.deduct_total_stock(item_id, qty)

    def finalize_purchase(self, item_id: str, qty: int) -> bool:
        # Finalizing purchase is allowed as part of the transaction flow
        return self._real.finalize_purchase(item_id, qty)

    def get_items_snapshot(self) -> list[dict[str, Any]]:
        return self._real.get_items_snapshot()

    # Expose the real manager for direct access
    @property
    def real(self) -> InventoryManager:
        return self._real
