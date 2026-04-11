# ============================================================
# Subsystem: Payment  Pattern: Adapter  Role: Digital wallet payment adapter
# ============================================================

from __future__ import annotations
from payment.i_payment_processor import IPaymentProcessor
from payment.legacy_stubs import LegacyDigitalWalletAPI


# PATTERN: Adapter
class DigitalWalletAdapter(IPaymentProcessor):
    def __init__(self) -> None:
        self._wallet = LegacyDigitalWalletAPI()

    def process_payment(self, amount: float, user_id: str) -> bool:
        result = self._wallet.deduct_balance(user_id, amount)
        return result == 0

    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        self._wallet.initiate_refund(transaction_id, amount)
        return True

    def get_provider_name(self) -> str:
        return "DigitalWallet"
