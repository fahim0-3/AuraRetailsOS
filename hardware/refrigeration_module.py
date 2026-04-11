# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Concrete decorator — refrigeration
# ============================================================

from __future__ import annotations
from hardware.kiosk_module_decorator import KioskModuleDecorator
from hardware.i_kiosk_module import IKioskModule


# PATTERN: Decorator (Concrete)
class RefrigerationModule(KioskModuleDecorator):
    def get_module_info(self) -> str:
        return f"{self._wrapped.get_module_info()} + [Refrigeration] active, temp: -4C"

    def is_operational(self) -> bool:
        return self._wrapped.is_operational()

    def perform_check(self) -> None:
        self._wrapped.perform_check()
        print("  RefrigerationModule: OK (-4C)")
