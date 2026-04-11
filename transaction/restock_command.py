# ============================================================
# Subsystem: Transaction  Pattern: Command  Role: Concrete command for restocking
# ============================================================

from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from transaction.i_command import ICommand
from core.central_registry import CentralRegistry

if TYPE_CHECKING:
    from inventory.i_inventory_manager import IInventoryManager


# PATTERN: Command (Concrete Command)
class RestockCommand(ICommand):
    def __init__(
        self,
        inventory: IInventoryManager,
        product_id: str,
        quantity: int,
    ) -> None:
        self._inventory = inventory
        self._product_id = product_id
        self._quantity = quantity
        self._status = "PENDING"
        self._timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def status(self) -> str:
        return self._status

    def get_description(self) -> str:
        return f"RESTOCK {self._product_id} +{self._quantity} [{self._status}]"

    def execute(self) -> bool:
        if self._inventory.restock(self._product_id, self._quantity):
            self._status = "SUCCESS"
            CentralRegistry.get_instance().log_event(
                f"RESTOCK SUCCESS: {self._product_id} +{self._quantity}"
            )
            return True
        self._status = "FAILED"
        return False

    def undo(self) -> bool:
        if self._status != "SUCCESS":
            return False
        # To undo a restock, we need to decrease total stock
        # We'll use a new method or direct deduction if we had one
        # For now, let's assume we can add 'decrease_total_stock' or use update_stock differently
        self._inventory.deduct_total_stock(self._product_id, self._quantity)
        self._status = "UNDONE"
        return True
