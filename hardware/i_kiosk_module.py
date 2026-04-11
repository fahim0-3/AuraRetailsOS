# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Component interface for kiosk modules
# ============================================================

from __future__ import annotations
from abc import ABC, abstractmethod


# PATTERN: Decorator (Component interface)
class IKioskModule(ABC):
    @abstractmethod
    def get_module_info(self) -> str: ...

    @abstractmethod
    def is_operational(self) -> bool: ...

    @abstractmethod
    def perform_check(self) -> None: ...
