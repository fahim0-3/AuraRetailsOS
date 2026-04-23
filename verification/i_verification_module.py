from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from inventory.i_inventory_item import IInventoryItem


class IVerificationModule(ABC):
    @abstractmethod
    def verify_purchase(
        self,
        item: IInventoryItem,
        user_id: str,
        quantity: int,
        context: dict[str, Any] | None = None,
    ) -> tuple[bool, str]: ...

