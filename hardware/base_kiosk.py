# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Concrete base component (no wrapping)
# ============================================================

from __future__ import annotations
from hardware.i_kiosk_module import IKioskModule


class BaseKiosk(IKioskModule):
    def get_module_info(self) -> str:
        return "[BaseKiosk] operational"

    def is_operational(self) -> bool:
        return True

    def perform_check(self) -> None:
        print("  BaseKiosk: OK")
