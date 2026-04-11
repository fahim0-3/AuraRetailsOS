# ============================================================
# Subsystem: Hardware  Pattern: Bridge  Role: Conveyor dispenser implementor
# ============================================================

from __future__ import annotations
from hardware.i_dispenser import IDispenserImpl


# PATTERN: Bridge (Concrete Implementor)
class ConveyorDispenserImpl(IDispenserImpl):
    def dispense_item(self, product_id: str, quantity: int) -> bool:
        print(f"  [ConveyorDispenser] Moving {quantity}x {product_id} along belt to collection port")
        return True

    def self_test(self) -> bool:
        print("  [ConveyorDispenser] Self-test: belt drive OK, photocell OK")
        return True

    def get_hardware_type(self) -> str:
        return "ConveyorDispenser"
