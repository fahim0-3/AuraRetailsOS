# ============================================================
# Subsystem: Factories  Pattern: Abstract Factory  Role: Concrete factory for pharmacy kiosks
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING

from core.abstract_kiosk_factory import AbstractKioskFactory
from hardware.robotic_arm_dispenser import RoboticArmDispenserImpl
from payment.credit_card_adapter import CreditCardAdapter
from inventory.inventory_proxy import InventoryProxy

if TYPE_CHECKING:
    from hardware.i_dispenser import IDispenserImpl
    from payment.i_payment_processor import IPaymentProcessor
    from inventory.i_inventory_manager import IInventoryManager


# PATTERN: Abstract Factory (Concrete factory)
class PharmacyKioskFactory(AbstractKioskFactory):
    def create_dispenser(self) -> IDispenserImpl:
        return RoboticArmDispenserImpl()

    def create_payment_processor(self) -> IPaymentProcessor:
        return CreditCardAdapter()

    def create_inventory_manager(self) -> IInventoryManager:
        return InventoryProxy("admin")

    def get_kiosk_type(self) -> str:
        return "PharmacyKiosk"
