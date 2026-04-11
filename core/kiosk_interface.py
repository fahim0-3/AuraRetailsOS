# ============================================================
# Subsystem: Core  Pattern: Facade  Role: Unified entry point for all kiosk interactions
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING

from core.abstract_kiosk_factory import AbstractKioskFactory
from hardware.dispenser_controller import DispenserController
from hardware.base_kiosk import BaseKiosk
from hardware.i_kiosk_module import IKioskModule
from hardware.i_dispenser import IDispenserImpl
from transaction.command_invoker import CommandInvoker
from transaction.purchase_item_command import PurchaseItemCommand
from transaction.refund_command import RefundCommand
from transaction.restock_command import RestockCommand
from inventory.product import Product
from inventory.product_bundle import ProductBundle

if TYPE_CHECKING:
    from payment.i_payment_processor import IPaymentProcessor
    from inventory.i_inventory_manager import IInventoryManager


# PATTERN: Facade
class KioskInterface:
    def __init__(self, factory: AbstractKioskFactory, kiosk_id: str) -> None:
        self._kiosk_id = kiosk_id
        self._kiosk_type = factory.get_kiosk_type()
        self._dispenser = DispenserController(factory.create_dispenser())
        self._payment = factory.create_payment_processor()
        self._inventory = factory.create_inventory_manager()
        self._module_chain: IKioskModule = BaseKiosk()
        self._invoker = CommandInvoker()

    @property
    def kiosk_id(self) -> str:
        return self._kiosk_id

    @property
    def kiosk_type(self) -> str:
        return self._kiosk_type

    def purchase_item(self, product_id: str, user_id: str, quantity: int) -> bool:
        cmd = PurchaseItemCommand(
            self._inventory,
            self._payment,
            self._dispenser,
            product_id,
            user_id,
            quantity,
        )
        return self._invoker.execute_command(cmd)

    def refund_transaction(self, transaction_id: str, amount: float) -> bool:
        cmd = RefundCommand(self._payment, transaction_id, amount)
        return self._invoker.execute_command(cmd)

    def restock_inventory(self, product_id: str, quantity: int) -> bool:
        cmd = RestockCommand(self._inventory, product_id, quantity)
        return self._invoker.execute_command(cmd)

    def run_diagnostics(self) -> None:
        print(f"  Kiosk: {self._kiosk_id} ({self._kiosk_type})")
        print(f"  Dispenser: {self._dispenser.current_hardware_type}")
        self._dispenser.run_self_test()
        self._module_chain.perform_check()

    def display_inventory(self) -> None:
        self._inventory.list_all()

    def swap_dispenser(self, new_impl: IDispenserImpl) -> None:
        self._dispenser.set_impl(new_impl)

    def attach_module(self, module: IKioskModule) -> None:
        # The module wraps the current chain — module's constructor takes the existing chain
        # But to attach in order, we need to wrap existing with new
        # The decorator pattern: new_module.__init__(existing_chain) sets _wrapped
        # Then we set module_chain to the new outermost module
        # Since module already wraps via its constructor, we just need to chain it
        # Actually, the decorator wraps via constructor — so we need to set _wrapped on the module
        # The cleanest approach: wrap the current chain inside the new module
        module._wrapped = self._module_chain  # type: ignore
        self._module_chain = module

    def print_transaction_history(self) -> None:
        self._invoker.print_history()

    # Convenience: get underlying inventory manager (needed for adding items in main.py)
    @property
    def inventory(self) -> IInventoryManager:
        return self._inventory

    # Allow setting payment (needed for Scenario 2 payment swap)
    @property
    def payment(self) -> IPaymentProcessor:
        return self._payment

    @payment.setter
    def payment(self, new_payment: IPaymentProcessor) -> None:
        self._payment = new_payment

    # Setup method: adds item directly to real manager (bypasses proxy auth for kiosk setup)
    def add_product(self, item: Product | ProductBundle) -> None:
        self._inventory.real.add_item(item)  # type: ignore
