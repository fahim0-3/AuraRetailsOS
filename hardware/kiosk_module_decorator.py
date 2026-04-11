# ============================================================
# Subsystem: Hardware  Pattern: Decorator  Role: Abstract decorator for kiosk modules
# ============================================================

from __future__ import annotations
from abc import ABC
from hardware.i_kiosk_module import IKioskModule


# PATTERN: Decorator (Abstract decorator)
class KioskModuleDecorator(IKioskModule):
    def __init__(self, module: IKioskModule) -> None:
        self._wrapped: IKioskModule = module
