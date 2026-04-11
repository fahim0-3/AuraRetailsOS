# ============================================================
# Subsystem: Core  Pattern: Abstract Factory  Role: Abstract factory interface
# ============================================================

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hardware.i_dispenser import IDispenserImpl
    from payment.i_payment_processor import IPaymentProcessor
    from inventory.i_inventory_manager import IInventoryManager


# PATTERN: Abstract Factory (Abstract factory interface)
class AbstractKioskFactory(ABC):
    @abstractmethod
    def create_dispenser(self) -> IDispenserImpl: ...

    @abstractmethod
    def create_payment_processor(self) -> IPaymentProcessor: ...

    @abstractmethod
    def create_inventory_manager(self) -> IInventoryManager: ...

    @abstractmethod
    def get_kiosk_type(self) -> str: ...
