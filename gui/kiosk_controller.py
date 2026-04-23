from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal

from core.abstract_kiosk_factory import AbstractKioskFactory
from core.central_registry import CentralRegistry
from core.kiosk_interface import KioskInterface
from hardware.i_dispenser import IDispenserImpl
from hardware.i_kiosk_module import IKioskModule
from inventory.product import Product
from inventory.product_bundle import ProductBundle
from payment.credit_card_adapter import CreditCardAdapter
from payment.digital_wallet_adapter import DigitalWalletAdapter
from payment.upi_adapter import UPIAdapter


class KioskController(QObject):
    purchase_result = Signal(bool, str)
    refund_result = Signal(bool, str)
    inventory_changed = Signal()
    history_changed = Signal()
    log_message = Signal(str)
    kiosk_changed = Signal()

    def __init__(self, factory: AbstractKioskFactory, kiosk_id: str) -> None:
        super().__init__()
        self._kiosk = KioskInterface(factory, kiosk_id)
        self._last_log_index = len(self.get_event_log())

    @property
    def kiosk(self) -> KioskInterface:
        return self._kiosk

    def create_kiosk(self, factory: AbstractKioskFactory, kiosk_id: str) -> None:
        self._kiosk = KioskInterface(factory, kiosk_id)
        CentralRegistry.get_instance().log_event(
            f"KIOSK CREATED: {kiosk_id} ({self._kiosk.kiosk_type})"
        )
        self.kiosk_changed.emit()
        self.inventory_changed.emit()
        self.history_changed.emit()
        self._emit_new_logs()

    def purchase(self, product_id: str, user_id: str, quantity: int) -> bool:
        if not product_id.strip():
            message = "Purchase failed: product ID is required."
            self.purchase_result.emit(False, message)
            return False
        if not user_id.strip():
            message = "Purchase failed: user ID is required."
            self.purchase_result.emit(False, message)
            return False
        if quantity <= 0:
            message = "Purchase failed: quantity must be greater than 0."
            self.purchase_result.emit(False, message)
            return False

        success = self._kiosk.purchase_item(product_id.strip(), user_id.strip(), quantity)
        provider = self._kiosk.payment.get_provider_name()
        message = (
            f"Purchase successful ({provider}): {product_id} x{quantity} for {user_id}."
            if success
            else f"Purchase failed: {product_id} x{quantity} for {user_id}."
        )
        self.purchase_result.emit(success, message)
        self.history_changed.emit()
        self.inventory_changed.emit()
        self._emit_new_logs()
        return success

    def refund(self, transaction_id: str, amount: float) -> bool:
        if not transaction_id.strip():
            message = "Refund failed: transaction ID is required."
            self.refund_result.emit(False, message)
            return False
        if amount <= 0:
            message = "Refund failed: amount must be greater than 0."
            self.refund_result.emit(False, message)
            return False

        success = self._kiosk.refund_transaction(transaction_id.strip(), amount)
        message = (
            f"Refund successful: {transaction_id} (${amount:.2f})."
            if success
            else f"Refund failed: {transaction_id}."
        )
        self.refund_result.emit(success, message)
        self.history_changed.emit()
        self._emit_new_logs()
        return success

    def restock(self, product_id: str, quantity: int) -> bool:
        if not product_id.strip() or quantity <= 0:
            return False
        success = self._kiosk.restock_inventory(product_id.strip(), quantity)
        if success:
            CentralRegistry.get_instance().log_event(
                f"RESTOCK REQUESTED: {product_id} +{quantity}"
            )
        self.inventory_changed.emit()
        self.history_changed.emit()
        self._emit_new_logs()
        return success

    def swap_dispenser(self, new_impl: IDispenserImpl) -> None:
        self._kiosk.swap_dispenser(new_impl)
        CentralRegistry.get_instance().log_event(
            f"DISPENSER SWAPPED: {new_impl.get_hardware_type()}"
        )
        self.kiosk_changed.emit()
        self._emit_new_logs()

    def attach_module(self, module: IKioskModule) -> None:
        self._kiosk.attach_module(module)
        CentralRegistry.get_instance().log_event(
            f"MODULE ATTACHED: {module.__class__.__name__}"
        )
        self.kiosk_changed.emit()
        self._emit_new_logs()

    def set_payment_provider(self, provider_name: str) -> None:
        provider_key = provider_name.strip().lower()
        if provider_key == "upi":
            payment = UPIAdapter()
        elif provider_key in {"credit card", "creditcard"}:
            payment = CreditCardAdapter()
        elif provider_key in {"digital wallet", "digitalwallet"}:
            payment = DigitalWalletAdapter()
        else:
            raise ValueError(f"Unsupported payment provider: {provider_name}")

        self._kiosk.payment = payment
        CentralRegistry.get_instance().log_event(
            f"PAYMENT SWAPPED: {payment.get_provider_name()}"
        )
        self.kiosk_changed.emit()
        self._emit_new_logs()

    def set_pricing_mode(self, mode: str) -> bool:
        success = self._kiosk.set_pricing_mode(mode)
        if success:
            CentralRegistry.get_instance().log_event(f"PRICING MODE SET: {mode}")
            self.kiosk_changed.emit()
            self._emit_new_logs()
        return success

    def set_emergency_mode(self, enabled: bool) -> None:
        self._kiosk.set_emergency_mode(enabled)
        CentralRegistry.get_instance().log_event(
            f"EMERGENCY MODE: {'ON' if enabled else 'OFF'}"
        )
        self.kiosk_changed.emit()
        self._emit_new_logs()

    def set_max_purchase_per_user(self, limit: int) -> bool:
        success = self._kiosk.set_max_purchase_per_user(limit)
        if success:
            CentralRegistry.get_instance().log_event(f"MAX PURCHASE/USER SET: {limit}")
            self.kiosk_changed.emit()
            self._emit_new_logs()
        return success

    def load_inventory_from_json(self, path: str) -> None:
        self._kiosk.load_inventory_from_file(path)
        CentralRegistry.get_instance().log_event(f"INVENTORY LOADED: {path}")
        self.inventory_changed.emit()
        self._emit_new_logs()

    def save_inventory_to_json(self, path: str) -> None:
        self._kiosk.save_inventory_to_file(path)
        CentralRegistry.get_instance().log_event(f"INVENTORY SAVED: {path}")
        self._emit_new_logs()

    def add_product(self, product: Product) -> bool:
        success = self._kiosk.add_product(product)
        if success:
            CentralRegistry.get_instance().log_event(
                f"PRODUCT ADDED: {product.item_id} ({product.name})"
            )
            self.inventory_changed.emit()
            self._emit_new_logs()
        return success

    def add_bundle(self, bundle_id: str, name: str, child_ids: list[str]) -> bool:
        if not bundle_id.strip() or not name.strip() or not child_ids:
            return False

        bundle = ProductBundle(bundle_id.strip(), name.strip())
        for child_id in child_ids:
            child = self._kiosk.inventory.get_item(child_id)
            if child is None:
                return False
            bundle.add_item(child)

        success = self._kiosk.add_product(bundle)
        if success:
            CentralRegistry.get_instance().log_event(
                f"BUNDLE ADDED: {bundle.item_id} ({len(child_ids)} children)"
            )
            self.inventory_changed.emit()
            self._emit_new_logs()
        return success

    def get_diagnostics_report(self) -> str:
        self._kiosk.run_diagnostics()
        data = self._kiosk.get_diagnostics_snapshot()
        lines = [
            f"Kiosk ID: {data['kiosk_id']}",
            f"Kiosk Type: {data['kiosk_type']}",
            f"Payment Provider: {self.get_payment_provider_display_name()}",
            f"Pricing Policy: {data['pricing_policy']}",
            f"Emergency Mode: {'ON' if data['emergency_mode'] else 'OFF'}",
            f"Max Purchase/User: {data['max_purchase_per_user']}",
            f"Dispenser: {data['dispenser_type']}",
            f"Module Chain: {data['module_info']}",
            f"Active Modules: {', '.join(data['active_modules'])}",
            f"Operational: {'YES' if data['module_operational'] else 'NO'}",
        ]
        return "\n".join(lines)

    def get_kiosk_snapshot(self) -> dict[str, Any]:
        return self._kiosk.get_diagnostics_snapshot()

    def get_inventory_snapshot(self) -> list[dict[str, Any]]:
        return self._kiosk.get_inventory_snapshot()

    def get_transaction_history(self) -> list[dict[str, Any]]:
        return self._kiosk.get_transaction_history()

    def get_event_log(self) -> list[str]:
        return self._kiosk.get_event_log()

    def get_payment_provider_display_name(self) -> str:
        provider = self._kiosk.payment.get_provider_name()
        if provider == "CreditCard":
            return "Credit Card"
        if provider == "DigitalWallet":
            return "Digital Wallet"
        return provider

    def _emit_new_logs(self) -> None:
        logs = self.get_event_log()
        for entry in logs[self._last_log_index:]:
            self.log_message.emit(entry)
        self._last_log_index = len(logs)

