# ============================================================
# Subsystem: Payment  Pattern: Adapter  Role: UPI payment adapter
# ============================================================

from __future__ import annotations
from payment.i_payment_processor import IPaymentProcessor
from payment.legacy_stubs import LegacyUPISystem


# PATTERN: Adapter
class UPIAdapter(IPaymentProcessor):
    def __init__(self) -> None:
        self._upi = LegacyUPISystem()

    def process_payment(self, amount: float, user_id: str) -> bool:
        vpa = f"{user_id}@zephyrus"
        return self._upi.send_upi_request(vpa, amount)

    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        return self._upi.raise_dispute(transaction_id)

    def get_provider_name(self) -> str:
        return "UPI"
