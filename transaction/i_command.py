# ============================================================
# Subsystem: Transaction  Pattern: Command  Role: Command interface
# ============================================================

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timezone


# PATTERN: Command (Interface)
class ICommand(ABC):
    @abstractmethod
    def execute(self) -> bool: ...

    @abstractmethod
    def undo(self) -> bool: ...

    @abstractmethod
    def get_description(self) -> str: ...

    @property
    @abstractmethod
    def timestamp(self) -> str: ...

    @property
    @abstractmethod
    def status(self) -> str: ...
