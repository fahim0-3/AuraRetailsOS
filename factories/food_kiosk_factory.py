# ============================================================
# Subsystem: Factories  Pattern: Abstract Factory  Role: Concrete factory for food kiosks
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING

from core.abstract_kiosk_factory import AbstractKioskFactory
from hardware.conveyor_dispenser import ConveyorDispenserImpl
from payment.upi_adapter import UPIAdapter
from inventory.inventory_proxy import InventoryProxy
from pricing.pricing_policies import DiscountPricingPolicy
from verification.kiosk_verification_module import KioskVerificationModule

if TYPE_CHECKING:
    from hardware.i_dispenser import IDispenserImpl
    from payment.i_payment_processor import IPaymentProcessor
    from inventory.i_inventory_manager import IInventoryManager
    from pricing.i_pricing_policy import IPricingPolicy
    from verification.i_verification_module import IVerificationModule


# PATTERN: Abstract Factory (Concrete factory)
class FoodKioskFactory(AbstractKioskFactory):
    def create_dispenser(self) -> IDispenserImpl:
        return ConveyorDispenserImpl()

    def create_payment_processor(self) -> IPaymentProcessor:
        return UPIAdapter()

    def create_inventory_manager(self) -> IInventoryManager:
        return InventoryProxy("user")

    def create_pricing_policy(self) -> IPricingPolicy:
        return DiscountPricingPolicy(0.10)

    def create_verification_module(self) -> IVerificationModule:
        return KioskVerificationModule()

    def get_kiosk_type(self) -> str:
        return "FoodKiosk"
