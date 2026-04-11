# ============================================================
# Subsystem: Payment  Pattern: Adapter  Role: Simulated incompatible third-party APIs
# ============================================================

from __future__ import annotations


# Simulate incompatible legacy credit card gateway
class LegacyCreditCardGateway:
    def authorize(self, amt: float, card_token: str) -> bool:
        self.last_transaction_ref = f"CC-{hash(card_token) % 100000}"
        return True

    def reverse_charge(self, txn_ref: str) -> bool:
        return True

    last_transaction_ref: str = ""


# Simulate incompatible digital wallet API
class LegacyDigitalWalletAPI:
    def deduct_balance(self, wallet_id: str, amount: float) -> int:
        """Returns int, not bool"""
        self.last_ref = f"DW-{hash(wallet_id) % 100000}"
        return 0  # 0 = success

    def initiate_refund(self, ref: str, amount: float) -> None:
        """void return"""
        self.last_ref = ref

    last_ref: str = ""


# Simulate incompatible UPI system
class LegacyUPISystem:
    def send_upi_request(self, vpa: str, rupees: float) -> bool:
        self.last_ref = f"UPI-{hash(vpa) % 100000}"
        return True

    def raise_dispute(self, upi_ref: str) -> bool:
        return True

    last_ref: str = ""
