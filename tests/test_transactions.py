# ============================================================
# Subsystem: Tests  Pattern: Testing  Role: Test transaction functionality
# ============================================================

import unittest
from unittest.mock import Mock
from transaction.purchase_item_command import PurchaseItemCommand
from transaction.refund_command import RefundCommand
from transaction.restock_command import RestockCommand
from transaction.command_invoker import CommandInvoker
from core.central_registry import CentralRegistry
from inventory.product import Product
from inventory.inventory_manager import InventoryManager
from inventory.inventory_proxy import InventoryProxy
from payment.credit_card_adapter import CreditCardAdapter
from hardware.dispenser_controller import DispenserController
from hardware.network_module import NetworkModule
from hardware.spiral_dispenser import SpiralDispenserImpl
from pricing.pricing_policies import DiscountPricingPolicy
from verification.kiosk_verification_module import KioskVerificationModule
from core.kiosk_interface import KioskInterface
from factories.food_kiosk_factory import FoodKioskFactory


class TestTransactions(unittest.TestCase):
    def setUp(self):
        # Clear CentralRegistry singleton for clean tests
        CentralRegistry._instance = None

        self.inventory = InventoryManager()
        self.payment = CreditCardAdapter()
        self.dispenser = DispenserController(SpiralDispenserImpl())
        self.invoker = CommandInvoker()

        # Create test product
        self.product = Product("TEST001", "Test Product", 25.0, total_stock=10, reserved_stock=0)
        self.inventory.add_item(self.product)

    def test_purchase_success(self):
        cmd = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "TEST001",
            "USER001",
            2
        )

        result = self.invoker.execute_command(cmd)
        self.assertTrue(result)
        self.assertEqual(cmd.status, "SUCCESS")
        self.assertEqual(self.product.get_available_stock(), 8)  # 10 - 2

    def test_purchase_insufficient_stock(self):
        cmd = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "TEST001",
            "USER001",
            15  # More than available
        )

        result = self.invoker.execute_command(cmd)
        self.assertFalse(result)
        self.assertEqual(cmd.status, "FAILED")
        self.assertEqual(self.product.get_available_stock(), 10)  # Unchanged

    def test_purchase_payment_failure(self):
        # Mock payment to fail
        mock_payment = Mock()
        mock_payment.process_payment.return_value = False

        cmd = PurchaseItemCommand(
            self.inventory,
            mock_payment,
            self.dispenser,
            "TEST001",
            "USER001",
            2
        )

        result = self.invoker.execute_command(cmd)
        self.assertFalse(result)
        self.assertEqual(cmd.status, "FAILED")
        # Stock should be rolled back
        self.assertEqual(self.product.get_available_stock(), 10)  # Unchanged

    def test_purchase_dispense_failure(self):
        # Mock dispenser to fail
        mock_dispenser = Mock()
        mock_dispenser.dispense.return_value = False

        cmd = PurchaseItemCommand(
            self.inventory,
            self.payment,
            mock_dispenser,
            "TEST001",
            "USER001",
            2
        )

        result = self.invoker.execute_command(cmd)
        self.assertFalse(result)
        self.assertEqual(cmd.status, "FAILED")
        # Stock should be rolled back and payment refunded
        self.assertEqual(self.product.get_available_stock(), 10)  # Unchanged

    def test_refund_command(self):
        # First make a purchase
        purchase_cmd = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "TEST001",
            "USER001",
            1
        )
        self.invoker.execute_command(purchase_cmd)

        # Then refund it
        refund_cmd = RefundCommand(self.payment, purchase_cmd._transaction_id, 25.0)
        result = self.invoker.execute_command(refund_cmd)
        self.assertTrue(result)
        self.assertEqual(refund_cmd.status, "SUCCESS")

    def test_restock_command(self):
        # First reduce stock
        self.inventory.update_stock("TEST001", -3)
        self.assertEqual(self.product.get_available_stock(), 7)

        # Then restock
        cmd = RestockCommand(self.inventory, "TEST001", 5)
        result = self.invoker.execute_command(cmd)
        self.assertTrue(result)
        self.assertEqual(self.product.get_available_stock(), 12)  # 7 + 5

    def test_command_undo(self):
        # Make a purchase
        cmd = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "TEST001",
            "USER001",
            2
        )
        self.invoker.execute_command(cmd)
        self.assertEqual(cmd.status, "SUCCESS")
        self.assertEqual(self.product.get_available_stock(), 8)

        # Undo the purchase
        result = self.invoker.undo_last()
        self.assertTrue(result)
        self.assertEqual(cmd.status, "UNDONE")
        self.assertEqual(self.product.get_available_stock(), 10)  # Restored

    def test_command_invoker_history(self):
        # Execute a few commands
        cmd1 = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "TEST001",
            "USER001",
            1
        )
        cmd2 = RestockCommand(self.inventory, "TEST001", 5)

        self.invoker.execute_command(cmd1)
        self.invoker.execute_command(cmd2)

        self.assertEqual(len(self.invoker._history), 2)
        self.assertEqual(self.invoker._history[0].status, "SUCCESS")
        self.assertEqual(self.invoker._history[1].status, "SUCCESS")

    def test_purchase_uses_discount_pricing_policy(self):
        cmd = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "TEST001",
            "USER001",
            2,
            pricing_policy=DiscountPricingPolicy(0.20),
        )
        result = self.invoker.execute_command(cmd)
        self.assertTrue(result)
        self.assertEqual(cmd.status, "SUCCESS")
        self.assertEqual(cmd._amount, 40.0)  # 25 * 2 with 20% discount

    def test_purchase_blocks_emergency_limit_for_essential_item(self):
        essential = Product(
            "ESS001",
            "Essential Product",
            12.0,
            total_stock=20,
            essential_item=True,
        )
        self.inventory.add_item(essential)
        verifier = KioskVerificationModule()

        cmd = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "ESS001",
            "USER001",
            3,
            verification_module=verifier,
            verification_context={
                "available_modules": {"base"},
                "emergency_mode": True,
                "max_purchase_per_user": 2,
            },
        )
        result = self.invoker.execute_command(cmd)
        self.assertFalse(result)
        self.assertEqual(cmd.status, "FAILED")
        self.assertEqual(essential.get_available_stock(), 20)

    def test_purchase_blocks_missing_required_hardware_module(self):
        cold_chain = Product(
            "COLD001",
            "Cold Chain Product",
            40.0,
            total_stock=5,
            required_modules=["refrigeration"],
        )
        self.inventory.add_item(cold_chain)
        verifier = KioskVerificationModule()

        cmd_fail = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "COLD001",
            "USER001",
            1,
            verification_module=verifier,
            verification_context={
                "available_modules": {"base"},
                "emergency_mode": False,
                "max_purchase_per_user": 5,
            },
        )
        result_fail = self.invoker.execute_command(cmd_fail)
        self.assertFalse(result_fail)

        cmd_success = PurchaseItemCommand(
            self.inventory,
            self.payment,
            self.dispenser,
            "COLD001",
            "USER001",
            1,
            verification_module=verifier,
            verification_context={
                "available_modules": {"base", "refrigeration"},
                "emergency_mode": False,
                "max_purchase_per_user": 5,
            },
        )
        result_success = self.invoker.execute_command(cmd_success)
        self.assertTrue(result_success)
        self.assertEqual(cmd_success.status, "SUCCESS")

    def test_purchase_blocks_when_kiosk_in_maintenance_mode(self):
        CentralRegistry.get_instance().set_status("kioskMode", "maintenance")
        kiosk = KioskInterface(FoodKioskFactory(), "KIOSK-TEST")
        kiosk.add_product(Product("FOOD001", "Snack", 10.0, total_stock=3))

        result = kiosk.purchase_item("FOOD001", "USER001", 1)

        self.assertFalse(result)
        self.assertEqual(kiosk.inventory.get_item("FOOD001").get_available_stock(), 3)
        self.assertTrue(
            any("maintenance mode" in event for event in CentralRegistry.get_instance().get_event_log())
        )

    def test_purchase_blocks_when_network_module_is_offline(self):
        CentralRegistry.get_instance().set_status("networkOnline", False)
        kiosk = KioskInterface(FoodKioskFactory(), "KIOSK-TEST")
        kiosk.attach_module(NetworkModule(kiosk._module_chain))
        kiosk.add_product(Product("FOOD002", "Wrap", 15.0, total_stock=4))

        result = kiosk.purchase_item("FOOD002", "USER001", 1)

        self.assertFalse(result)
        self.assertEqual(kiosk.inventory.get_item("FOOD002").get_available_stock(), 4)
        self.assertTrue(
            any("network is offline" in event for event in CentralRegistry.get_instance().get_event_log())
        )


if __name__ == '__main__':
    unittest.main()
