# ============================================================
# Subsystem: Hardware  Pattern: Bridge  Role: Spiral dispenser implementor
# ============================================================

from __future__ import annotations
from hardware.i_dispenser import IDispenserImpl


# PATTERN: Bridge (Concrete Implementor)
class SpiralDispenserImpl(IDispenserImpl):
    def dispense_item(self, product_id: str, quantity: int) -> bool:
        print(f"  [SpiralDispenser] Dispensing {quantity}x {product_id} via rotating spiral")
        return True

    def self_test(self) -> bool:
        print("  [SpiralDispenser] Self-test: spiral motor OK, sensor OK")
        return True

    def get_hardware_type(self) -> str:
        return "SpiralDispenser"
