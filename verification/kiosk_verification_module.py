from __future__ import annotations

from typing import TYPE_CHECKING, Any

from verification.i_verification_module import IVerificationModule

if TYPE_CHECKING:
    from inventory.i_inventory_item import IInventoryItem


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _to_positive_int(value: Any, default: int) -> int:
    try:
        as_int = int(value)
        return as_int if as_int > 0 else default
    except (TypeError, ValueError):
        return default


class KioskVerificationModule(IVerificationModule):
    def verify_purchase(
        self,
        item: IInventoryItem,
        user_id: str,
        quantity: int,
        context: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        del user_id
        ctx = context or {}

        if quantity <= 0:
            return False, "quantity must be greater than zero"

        kiosk_mode = str(ctx.get("kiosk_mode", "service") or "service").strip().lower()
        if kiosk_mode in {"maintenance", "offline", "disabled"}:
            return False, f"kiosk is not accepting purchases while in {kiosk_mode} mode"

        requires_network = _to_bool(ctx.get("requires_network", False))
        if requires_network and not _to_bool(ctx.get("network_online", True)):
            return False, "network is offline"

        if not _to_bool(ctx.get("kiosk_operational", True)):
            return False, "kiosk is not operational"

        available_modules = {
            str(module_key).strip().lower()
            for module_key in ctx.get("available_modules", set())
            if str(module_key).strip()
        }
        missing = sorted(self._collect_missing_modules(item, available_modules))
        if missing:
            return False, f"missing required hardware module(s): {', '.join(missing)}"

        emergency_mode = _to_bool(ctx.get("emergency_mode", False))
        if emergency_mode and self._contains_essential_item(item):
            max_limit = _to_positive_int(ctx.get("max_purchase_per_user", 1), 1)
            if quantity > max_limit:
                return (
                    False,
                    f"emergency purchase limit exceeded for essential item (max={max_limit})",
                )

        return True, "verification passed"

    def _collect_missing_modules(
        self,
        item: IInventoryItem,
        available_modules: set[str],
    ) -> set[str]:
        if item.is_bundle():
            missing: set[str] = set()
            for child in item._children:  # type: ignore[attr-defined]
                missing.update(self._collect_missing_modules(child, available_modules))
            return missing

        required_modules = {
            str(module).strip().lower()
            for module in getattr(item, "required_modules", [])
            if str(module).strip()
        }
        return required_modules - available_modules

    def _contains_essential_item(self, item: IInventoryItem) -> bool:
        if item.is_bundle():
            return any(self._contains_essential_item(child) for child in item._children)  # type: ignore[attr-defined]
        return bool(getattr(item, "is_essential_item", False))

