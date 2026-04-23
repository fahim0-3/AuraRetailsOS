# ============================================================
# Subsystem: Core  Pattern: Facade  Role: Unified entry point for all kiosk interactions
# ============================================================

from __future__ import annotations
from typing import TYPE_CHECKING, Any

from core.abstract_kiosk_factory import AbstractKioskFactory
from core.central_registry import CentralRegistry
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
from pricing.i_pricing_policy import IPricingPolicy
from pricing.pricing_policies import (
    DiscountPricingPolicy,
    EmergencyPricingPolicy,
    StandardPricingPolicy,
)
from verification.i_verification_module import IVerificationModule

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
        self._verification_module = factory.create_verification_module()
        self._default_pricing_policy = factory.create_pricing_policy()
        self._pricing_policies: dict[str, IPricingPolicy] = {
            "standard": StandardPricingPolicy(),
            "discount": DiscountPricingPolicy(),
            "emergency": EmergencyPricingPolicy(),
        }
        self._module_chain: IKioskModule = BaseKiosk()
        self._invoker = CommandInvoker()

    @property
    def kiosk_id(self) -> str:
        return self._kiosk_id

    @property
    def kiosk_type(self) -> str:
        return self._kiosk_type

    def purchase_item(self, product_id: str, user_id: str, quantity: int) -> bool:
        pricing_policy = self._resolve_pricing_policy()
        active_modules = self._get_active_module_keys()
        cmd = PurchaseItemCommand(
            self._inventory,
            self._payment,
            self._dispenser,
            product_id,
            user_id,
            quantity,
            pricing_policy=pricing_policy,
            verification_module=self._verification_module,
            pricing_context={
                "kiosk_type": self._kiosk_type,
                "emergency_mode": self._is_emergency_mode(),
            },
            verification_context={
                "available_modules": active_modules,
                "emergency_mode": self._is_emergency_mode(),
                "max_purchase_per_user": self._get_max_purchase_per_user(),
                "kiosk_mode": self._get_kiosk_mode(),
                "kiosk_operational": self._module_chain.is_operational(),
                "requires_network": "network" in active_modules,
                "network_online": self._is_network_online(),
            },
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

    def get_transaction_history(self) -> list[dict[str, Any]]:
        return self._invoker.get_history()

    def get_event_log(self) -> list[str]:
        return CentralRegistry.get_instance().get_event_log()

    def get_inventory_snapshot(self) -> list[dict[str, Any]]:
        manager = self._get_real_inventory_manager()
        if hasattr(manager, "get_items_snapshot"):
            return manager.get_items_snapshot()  # type: ignore[no-any-return]
        return []

    def get_diagnostics_snapshot(self) -> dict[str, Any]:
        active_policy = self._resolve_pricing_policy()
        return {
            "kiosk_id": self._kiosk_id,
            "kiosk_type": self._kiosk_type,
            "dispenser_type": self._dispenser.current_hardware_type,
            "module_info": self._module_chain.get_module_info(),
            "module_operational": self._module_chain.is_operational(),
            "payment_provider": self._payment.get_provider_name(),
            "pricing_policy": active_policy.policy_name,
            "verification_module": self._verification_module.__class__.__name__,
            "emergency_mode": self._is_emergency_mode(),
            "max_purchase_per_user": self._get_max_purchase_per_user(),
            "active_modules": sorted(self._get_active_module_keys()),
            "kiosk_mode": self._get_kiosk_mode(),
            "network_online": self._is_network_online(),
        }

    def load_inventory_from_file(self, filepath: str) -> None:
        manager = self._get_real_inventory_manager()
        manager.load_from_file(filepath)  # type: ignore[attr-defined]

    def save_inventory_to_file(self, filepath: str) -> None:
        manager = self._get_real_inventory_manager()
        manager.save_to_file(filepath)  # type: ignore[attr-defined]

    def _get_real_inventory_manager(self) -> IInventoryManager:
        return getattr(self._inventory, "real", self._inventory)

    def _resolve_pricing_policy(self) -> IPricingPolicy:
        if self._is_emergency_mode():
            return self._pricing_policies["emergency"]

        selected = CentralRegistry.get_instance().get_status("pricingMode")
        key = str(selected).strip().lower() if selected is not None else ""
        if key in self._pricing_policies:
            return self._pricing_policies[key]
        return self._default_pricing_policy

    def _is_emergency_mode(self) -> bool:
        value = CentralRegistry.get_instance().get_status("emergencyMode")
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return False

    def _get_max_purchase_per_user(self) -> int:
        value = CentralRegistry.get_instance().get_status("maxPurchasePerUser")
        try:
            parsed = int(value)  # type: ignore[arg-type]
            return parsed if parsed > 0 else 5
        except (TypeError, ValueError):
            return 5

    def _get_kiosk_mode(self) -> str:
        value = CentralRegistry.get_instance().get_status("kioskMode")
        if value is None:
            return "service"
        text = str(value).strip().lower()
        return text or "service"

    def _is_network_online(self) -> bool:
        value = CentralRegistry.get_instance().get_status("networkOnline")
        if value is None:
            return True
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on", "online"}
        return bool(value)

    def _get_active_module_keys(self) -> set[str]:
        modules: set[str] = set()
        node: IKioskModule | None = self._module_chain
        while node is not None:
            module_key = getattr(node, "MODULE_KEY", node.__class__.__name__)
            modules.add(str(module_key).strip().lower())
            node = getattr(node, "_wrapped", None)
        return modules

    def set_pricing_mode(self, mode: str) -> bool:
        key = mode.strip().lower()
        if key not in self._pricing_policies:
            return False
        CentralRegistry.get_instance().set_status("pricingMode", key)
        return True

    def set_emergency_mode(self, enabled: bool) -> None:
        CentralRegistry.get_instance().set_status("emergencyMode", bool(enabled))

    def set_max_purchase_per_user(self, limit: int) -> bool:
        if limit <= 0:
            return False
        CentralRegistry.get_instance().set_status("maxPurchasePerUser", int(limit))
        return True

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
    def add_product(self, item: Product | ProductBundle) -> bool:
        return self._get_real_inventory_manager().add_item(item)
