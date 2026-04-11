# ============================================================
# Subsystem: Hardware  Pattern: Bridge  Role: Abstraction for dispenser hardware
# ============================================================

from __future__ import annotations
from hardware.i_dispenser import IDispenserImpl


# PATTERN: Bridge (Abstraction)
class DispenserController:
    def __init__(self, impl: IDispenserImpl) -> None:
        self._impl = impl

    def set_impl(self, new_impl: IDispenserImpl) -> None:
        """Hot-swap the dispenser implementation at runtime."""
        self._impl = new_impl
        print(f"[BRIDGE] Dispenser hot-swapped to: {new_impl.get_hardware_type()} — no system restart required")

    def dispense(self, product_id: str, qty: int) -> bool:
        return self._impl.dispense_item(product_id, qty)

    def run_self_test(self) -> bool:
        return self._impl.self_test()

    @property
    def current_hardware_type(self) -> str:
        return self._impl.get_hardware_type()
