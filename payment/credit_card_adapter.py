# ============================================================
# Subsystem: Payment  Pattern: Adapter  Role: Credit card payment adapter
# ============================================================

from __future__ import annotations
from payment.i_payment_processor import IPaymentProcessor
from payment.legacy_stubs import LegacyCreditCardGateway


# PATTERN: Adapter
class CreditCardAdapter(IPaymentProcessor):
    def __init__(self) -> None:
        self._gateway = LegacyCreditCardGateway()

    def process_payment(self, amount: float, user_id: str) -> bool:
        card_token = f"token_{user_id}"
        return self._gateway.authorize(amount, card_token)

    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        return self._gateway.reverse_charge(transaction_id)

    def get_provider_name(self) -> str:
        return "CreditCard"
