from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pricing.i_pricing_policy import IPricingPolicy

if TYPE_CHECKING:
    from inventory.i_inventory_item import IInventoryItem


def _is_essential_item(item: IInventoryItem) -> bool:
    if item.is_bundle():
        return any(_is_essential_item(child) for child in item._children)  # type: ignore[attr-defined]
    return bool(getattr(item, "is_essential_item", False))


class StandardPricingPolicy(IPricingPolicy):
    @property
    def policy_name(self) -> str:
        return "standard"

    def compute_price(
        self,
        item: IInventoryItem,
        quantity: int,
        context: dict[str, Any] | None = None,
    ) -> float:
        return round(item.price * quantity, 2)


class DiscountPricingPolicy(IPricingPolicy):
    def __init__(self, discount_rate: float = 0.10) -> None:
        self._discount_rate = max(0.0, min(discount_rate, 0.95))

    @property
    def policy_name(self) -> str:
        return "discount"

    def compute_price(
        self,
        item: IInventoryItem,
        quantity: int,
        context: dict[str, Any] | None = None,
    ) -> float:
        base = item.price * quantity
        return round(base * (1.0 - self._discount_rate), 2)


class EmergencyPricingPolicy(IPricingPolicy):
    def __init__(
        self,
        essential_discount_rate: float = 0.20,
        non_essential_markup_rate: float = 0.15,
    ) -> None:
        self._essential_discount_rate = max(0.0, min(essential_discount_rate, 0.95))
        self._non_essential_markup_rate = max(0.0, min(non_essential_markup_rate, 5.0))

    @property
    def policy_name(self) -> str:
        return "emergency"

    def compute_price(
        self,
        item: IInventoryItem,
        quantity: int,
        context: dict[str, Any] | None = None,
    ) -> float:
        base = item.price * quantity
        if _is_essential_item(item):
            return round(base * (1.0 - self._essential_discount_rate), 2)
        return round(base * (1.0 + self._non_essential_markup_rate), 2)

