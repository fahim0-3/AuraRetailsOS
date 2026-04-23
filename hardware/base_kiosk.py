# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Concrete base component (no wrapping)
# ============================================================

from __future__ import annotations
from core.central_registry import CentralRegistry
from hardware.i_kiosk_module import IKioskModule


class BaseKiosk(IKioskModule):
    MODULE_KEY = "base"

    def get_module_info(self) -> str:
        return "[BaseKiosk] operational"

    def is_operational(self) -> bool:
        registry = CentralRegistry.get_instance()
        mode = str(registry.get_status("kioskMode") or "service").strip().lower()
        if mode in {"maintenance", "offline", "disabled"}:
            return False

        hardware_status = registry.get_status("hardwareOperational")
        if hardware_status is None:
            return True
        if isinstance(hardware_status, bool):
            return hardware_status
        if isinstance(hardware_status, (int, float)):
            return bool(hardware_status)
        if isinstance(hardware_status, str):
            return hardware_status.strip().lower() in {"1", "true", "yes", "on", "ok"}
        return bool(hardware_status)

    def perform_check(self) -> None:
        print("  BaseKiosk: OK")
