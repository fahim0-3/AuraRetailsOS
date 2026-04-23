from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from inventory.i_inventory_item import IInventoryItem


class IPricingPolicy(ABC):
    @property
    @abstractmethod
    def policy_name(self) -> str: ...

    @abstractmethod
    def compute_price(
        self,
        item: IInventoryItem,
        quantity: int,
        context: dict[str, Any] | None = None,
    ) -> float: ...

