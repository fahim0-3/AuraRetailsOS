# ============================================================
# Subsystem: Transaction  Pattern: Command  Role: Concrete command for refunds
# ============================================================

from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from transaction.i_command import ICommand
from core.central_registry import CentralRegistry

if TYPE_CHECKING:
    from payment.i_payment_processor import IPaymentProcessor


# PATTERN: Command (Concrete Command)
class RefundCommand(ICommand):
    def __init__(
        self,
        payment: IPaymentProcessor,
        transaction_id: str,
        amount: float,
    ) -> None:
        self._payment = payment
        self._transaction_id = transaction_id
        self._amount = amount
        self._status = "PENDING"
        self._timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def status(self) -> str:
        return self._status

    def get_description(self) -> str:
        return f"REFUND {self._transaction_id} @ ${self._amount:.2f} [{self._status}]"

    def execute(self) -> bool:
        if self._amount <= 0:
            self._status = "FAILED"
            CentralRegistry.get_instance().log_event(
                f"REFUND FAILED: {self._transaction_id} (amount must be positive)"
            )
            return False

        if self._payment.refund_payment(self._transaction_id, self._amount):
            self._status = "SUCCESS"
            CentralRegistry.get_instance().log_event(
                f"REFUND SUCCESS: {self._transaction_id} @ ${self._amount:.2f}"
            )
            return True
        self._status = "FAILED"
        CentralRegistry.get_instance().log_event(
            f"REFUND FAILED: {self._transaction_id}"
        )
        return False

    def undo(self) -> bool:
        if self._status != "SUCCESS":
            return False
        self._status = "UNDONE"
        return True
