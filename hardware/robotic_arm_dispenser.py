# ============================================================
# Subsystem: Hardware  Pattern: Bridge  Role: Robotic arm dispenser implementor
# ============================================================

from __future__ import annotations
from hardware.i_dispenser import IDispenserImpl


# PATTERN: Bridge (Concrete Implementor)
class RoboticArmDispenserImpl(IDispenserImpl):
    def dispense_item(self, product_id: str, quantity: int) -> bool:
        print(f"  [RoboticArmDispenser] Pick-and-place {quantity}x {product_id} with 6-DOF arm")
        return True

    def self_test(self) -> bool:
        print("  [RoboticArmDispenser] Self-test: joints OK, gripper calibration OK")
        return True

    def get_hardware_type(self) -> str:
        return "RoboticArmDispenser"
