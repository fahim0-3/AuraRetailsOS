# ============================================================
# Subsystem: Payment  Pattern: Adapter  Role: Target interface for payment processors
# ============================================================

from __future__ import annotations
from abc import ABC, abstractmethod


# PATTERN: Adapter (Target interface)
class IPaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float, user_id: str) -> bool: ...

    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: float) -> bool: ...

    @abstractmethod
    def get_provider_name(self) -> str: ...
