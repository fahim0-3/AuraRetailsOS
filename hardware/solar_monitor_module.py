# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Concrete decorator — solar monitoring
# ============================================================

from __future__ import annotations
from hardware.kiosk_module_decorator import KioskModuleDecorator
from hardware.i_kiosk_module import IKioskModule


# PATTERN: Decorator (Concrete)
class SolarMonitorModule(KioskModuleDecorator):
    def get_module_info(self) -> str:
        return f"{self._wrapped.get_module_info()} + [Solar] output: 220W"

    def is_operational(self) -> bool:
        return self._wrapped.is_operational()

    def perform_check(self) -> None:
        self._wrapped.perform_check()
        print("  SolarMonitorModule: OK (220W)")
