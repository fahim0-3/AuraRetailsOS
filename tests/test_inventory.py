# ============================================================
# Subsystem: Tests  Pattern: Testing  Role: Test inventory functionality
# ============================================================

import unittest
from inventory.product import Product
from inventory.product_bundle import ProductBundle
from inventory.inventory_manager import InventoryManager
from inventory.inventory_proxy import InventoryProxy


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.manager = InventoryManager()
        self.proxy_admin = InventoryProxy("admin")
        self.proxy_user = InventoryProxy("user")

        # Create test products
        self.product1 = Product("P001", "Product 1", 10.0, total_stock=100, reserved_stock=0)
        self.product2 = Product("P002", "Product 2", 20.0, total_stock=50, reserved_stock=0)

        # Add products to manager
        self.manager.add_item(self.product1)
        self.manager.add_item(self.product2)

        # Create a bundle
        self.bundle = ProductBundle("B001", "Test Bundle")
        self.bundle.add_item(self.product1)
        self.bundle.add_item(self.product2)
        self.manager.add_item(self.bundle)

    def test_product_creation(self):
        self.assertEqual(self.product1.item_id, "P001")
        self.assertEqual(self.product1.name, "Product 1")
        self.assertEqual(self.product1.price, 10.0)
        self.assertEqual(self.product1.get_available_stock(), 100)
        self.assertTrue(self.product1.is_available())
        self.assertFalse(self.product1.is_bundle())

    def test_bundle_creation(self):
        self.assertEqual(self.bundle.item_id, "B001")
        self.assertEqual(self.bundle.name, "Test Bundle")
        self.assertEqual(self.bundle.price, 30.0)  # 10.0 + 20.0
        self.assertEqual(self.bundle.get_available_stock(), 50)  # min(100, 50)
        self.assertTrue(self.bundle.is_available())
        self.assertTrue(self.bundle.is_bundle())

    def test_stock_reservation(self):
        # Reserve 10 of product1
        result = self.manager.update_stock("P001", -10)
        self.assertTrue(result)
        self.assertEqual(self.product1.get_available_stock(), 90)

        # Try to reserve more than available
        result = self.manager.update_stock("P001", -95)
        self.assertFalse(result)
        self.assertEqual(self.product1.get_available_stock(), 90)  # Should remain unchanged

    def test_bundle_stock_calculation(self):
        # Reserve some of product1
        self.manager.update_stock("P001", -50)
        # Bundle stock should be min(50, 50) = 50
        self.assertEqual(self.bundle.get_available_stock(), 50)

        # Reserve some of product2
        self.manager.update_stock("P002", -25)
        # Bundle stock should be min(50, 25) = 25
        self.assertEqual(self.bundle.get_available_stock(), 25)

    def test_proxy_authorization(self):
        # Admin should be able to add items
        new_product = Product("P003", "Product 3", 15.0, total_stock=20)
        result = self.proxy_admin.add_item(new_product)
        self.assertTrue(result)

        # User should NOT be able to add items
        new_product2 = Product("P004", "Product 4", 25.0, total_stock=10)
        result = self.proxy_user.add_item(new_product2)
        self.assertFalse(result)

        # Use a shared inventory manager for testing proxy authorization
        shared_manager = InventoryManager()
        proxy_admin = InventoryProxy("admin")
        proxy_user = InventoryProxy("user")
        proxy_tech = InventoryProxy("technician")

        # Override the real managers to use the shared one
        proxy_admin._real = shared_manager
        proxy_user._real = shared_manager
        proxy_tech._real = shared_manager

        # Add test product via admin (only admin can add)
        test_product = Product("P001", "Product 1", 10.0, total_stock=100, reserved_stock=0)
        result_admin = proxy_admin.add_item(test_product)
        self.assertTrue(result_admin)
        # Verify the product was actually added
        self.assertIsNotNone(shared_manager.get_item("P001"))

        # Technician should be able to update stock (positive delta = restock)
        result = proxy_tech.update_stock("P001", 10)  # Restock
        self.assertTrue(result)

        # User should NOT be able to restock (positive delta)
        result = proxy_user.update_stock("P001", 10)  # Restock
        self.assertFalse(result)

        # But user should be able to make reservations (negative delta)
        result = proxy_user.update_stock("P001", -5)  # Reserve
        self.assertTrue(result)  # Reservations allowed for all roles


if __name__ == '__main__':
    unittest.main()