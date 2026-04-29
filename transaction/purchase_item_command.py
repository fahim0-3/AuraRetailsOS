# ============================================================
# Subsystem: Transaction  Pattern: Command  Role: Concrete command for purchasing items
# ============================================================

from __future__ import annotations
from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING, Any

from transaction.i_command import ICommand
from core.central_registry import CentralRegistry

if TYPE_CHECKING:
    from inventory.i_inventory_manager import IInventoryManager
    from inventory.i_inventory_item import IInventoryItem
    from payment.i_payment_processor import IPaymentProcessor
    from hardware.dispenser_controller import DispenserController
    from pricing.i_pricing_policy import IPricingPolicy
    from verification.i_verification_module import IVerificationModule


# PATTERN: Command (Concrete Command)
class PurchaseItemCommand(ICommand):
    def __init__(
        self,
        inventory: IInventoryManager,
        payment: IPaymentProcessor,
        dispenser: DispenserController,
        product_id: str,
        user_id: str,
        quantity: int,
        pricing_policy: IPricingPolicy | None = None,
        verification_module: IVerificationModule | None = None,
        pricing_context: dict[str, Any] | None = None,
        verification_context: dict[str, Any] | None = None,
    ) -> None:
        self._inventory = inventory
        self._payment = payment
        self._dispenser = dispenser
        self._product_id = product_id
        self._user_id = user_id
        self._quantity = quantity
        self._pricing_policy = pricing_policy
        self._verification_module = verification_module
        self._pricing_context = pricing_context or {}
        self._verification_context = verification_context or {}
        self._amount = 0.0
        self._transaction_id = str(uuid.uuid4())[:8].upper()
        self._status = "PENDING"
        self._timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def status(self) -> str:
        return self._status

    def get_description(self) -> str:
        return f"PURCHASE {self._product_id} x{self._quantity} @ ${self._amount:.2f} [{self._status}]"

    def execute(self) -> bool:
        # Step 1: get item and check availability
        item = self._inventory.get_item(self._product_id)
        if not item or not item.is_available():
            self._status = "FAILED"
            CentralRegistry.get_instance().log_event(
                f"PURCHASE FAILED: {self._product_id} — item unavailable"
            )
            return False

        if self._verification_module:
            verified, reason = self._verification_module.verify_purchase(
                item,
                self._user_id,
                self._quantity,
                self._verification_context,
            )
            if not verified:
                self._status = "FAILED"
                CentralRegistry.get_instance().log_event(
                    f"PURCHASE FAILED: {self._product_id} — {reason}"
                )
                return False

        self._amount = self._compute_final_price(item)

        # Step 2: reserve stock (tentative)
        if not self._inventory.update_stock(self._product_id, -self._quantity):
            self._status = "FAILED"
            CentralRegistry.get_instance().log_event(
                f"PURCHASE FAILED: {self._product_id} — stock reservation failed"
            )
            return False

        # Step 3: process payment
        if not self._payment.process_payment(self._amount, self._user_id):
            self._inventory.update_stock(self._product_id, self._quantity)  # rollback
            self._status = "FAILED"
            CentralRegistry.get_instance().log_event(
                f"PURCHASE FAILED: {self._product_id} — payment declined"
            )
            return False

        # Step 4: dispense
        if not self._dispenser.dispense(self._product_id, self._quantity):
            self._payment.refund_payment(self._transaction_id, self._amount)
            self._inventory.update_stock(self._product_id, self._quantity)  # rollback
            self._status = "FAILED"
            CentralRegistry.get_instance().log_event(
                f"PURCHASE FAILED: {self._product_id} — dispense failed"
            )
            return False

        self._inventory.finalize_purchase(self._product_id, self._quantity)
        self._status = "SUCCESS"
        CentralRegistry.get_instance().log_event(
            f"PURCHASE SUCCESS: {self._product_id} x{self._quantity} @ ${self._amount:.2f} [TXN: {self._transaction_id}]"
        )
        return True

    def _compute_final_price(self, item: IInventoryItem) -> float:
        if self._pricing_policy is None:
            return round(item.price * self._quantity, 2)
        return round(
            self._pricing_policy.compute_price(item, self._quantity, self._pricing_context),
            2,
        )

    def undo(self) -> bool:
        if self._status != "SUCCESS":
            return False
        self._payment.refund_payment(self._transaction_id, self._amount)
        self._inventory.restock(self._product_id, self._quantity)
        self._status = "UNDONE"
        CentralRegistry.get_instance().log_event(
            f"PURCHASE UNDONE: {self._product_id} x{self._quantity} [TXN: {self._transaction_id}]"
        )
        return True
