# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Concrete decorator — network connectivity
# ============================================================

from __future__ import annotations
from hardware.kiosk_module_decorator import KioskModuleDecorator
from hardware.i_kiosk_module import IKioskModule


# PATTERN: Decorator (Concrete)
class NetworkModule(KioskModuleDecorator):
    def get_module_info(self) -> str:
        return f"{self._wrapped.get_module_info()} + [Network] signal: strong"

    def is_operational(self) -> bool:
        return self._wrapped.is_operational()

    def perform_check(self) -> None:
        self._wrapped.perform_check()
        print("  NetworkModule: OK (signal: strong)")
