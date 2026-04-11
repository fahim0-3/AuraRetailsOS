# ============================================================
# Subsystem: Hardware  Pattern: Bridge  Role: Implementor interface for dispensers
# ============================================================

from __future__ import annotations
from abc import ABC, abstractmethod


# PATTERN: Bridge (Implementor interface)
class IDispenserImpl(ABC):
    @abstractmethod
    def dispense_item(self, product_id: str, quantity: int) -> bool: ...

    @abstractmethod
    def self_test(self) -> bool: ...

    @abstractmethod
    def get_hardware_type(self) -> str: ...
