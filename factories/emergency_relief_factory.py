# ============================================================
# Subsystem: Factories  Pattern: Abstract Factory  Role: Concrete factory for emergency relief kiosks
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING

from core.abstract_kiosk_factory import AbstractKioskFactory
from hardware.spiral_dispenser import SpiralDispenserImpl
from payment.digital_wallet_adapter import DigitalWalletAdapter
from inventory.inventory_proxy import InventoryProxy
from pricing.pricing_policies import EmergencyPricingPolicy
from verification.kiosk_verification_module import KioskVerificationModule

if TYPE_CHECKING:
    from hardware.i_dispenser import IDispenserImpl
    from payment.i_payment_processor import IPaymentProcessor
    from inventory.i_inventory_manager import IInventoryManager
    from pricing.i_pricing_policy import IPricingPolicy
    from verification.i_verification_module import IVerificationModule


# PATTERN: Abstract Factory (Concrete factory)
class EmergencyReliefKioskFactory(AbstractKioskFactory):
    def create_dispenser(self) -> IDispenserImpl:
        return SpiralDispenserImpl()

    def create_payment_processor(self) -> IPaymentProcessor:
        return DigitalWalletAdapter()

    def create_inventory_manager(self) -> IInventoryManager:
        return InventoryProxy("technician")

    def create_pricing_policy(self) -> IPricingPolicy:
        return EmergencyPricingPolicy()

    def create_verification_module(self) -> IVerificationModule:
        return KioskVerificationModule()

    def get_kiosk_type(self) -> str:
        return "EmergencyReliefKiosk"
