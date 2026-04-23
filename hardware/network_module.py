# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Concrete decorator — network connectivity
# ============================================================

from __future__ import annotations
from core.central_registry import CentralRegistry
from hardware.kiosk_module_decorator import KioskModuleDecorator
from hardware.i_kiosk_module import IKioskModule


# PATTERN: Decorator (Concrete)
class NetworkModule(KioskModuleDecorator):
    MODULE_KEY = "network"

    def get_module_info(self) -> str:
        return f"{self._wrapped.get_module_info()} + [Network] signal: strong"

    def is_operational(self) -> bool:
        if not self._wrapped.is_operational():
            return False

        network_status = CentralRegistry.get_instance().get_status("networkOnline")
        if network_status is None:
            return True
        if isinstance(network_status, bool):
            return network_status
        if isinstance(network_status, (int, float)):
            return bool(network_status)
        if isinstance(network_status, str):
            return network_status.strip().lower() in {"1", "true", "yes", "on", "online"}
        return bool(network_status)

    def perform_check(self) -> None:
        self._wrapped.perform_check()
        print("  NetworkModule: OK (signal: strong)")
