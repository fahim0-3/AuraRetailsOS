import os
import tempfile
import unittest

from core.central_registry import CentralRegistry
from factories.pharmacy_kiosk_factory import PharmacyKioskFactory
from gui.kiosk_controller import KioskController


class TestRoleAuthentication(unittest.TestCase):
    def setUp(self) -> None:
        CentralRegistry._instance = None
        self.registry = CentralRegistry.get_instance()
        self.registry.set_status(
            "rolePasswords",
            {
                "admin": "admin123",
                "technician": "tech123",
            },
        )

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        temp_file.close()
        self.config_path = temp_file.name

        self.controller = KioskController(PharmacyKioskFactory(), "KIOSK-001")
        self.controller._config_path = self.config_path

    def tearDown(self) -> None:
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_user_role_changes_without_password(self) -> None:
        self.assertTrue(self.controller.set_operator_role("user"))
        self.assertEqual(self.controller.get_operator_role(), "user")

    def test_admin_role_requires_correct_password(self) -> None:
        self.controller.set_operator_role("user")
        current_role = self.controller.get_operator_role()
        self.assertFalse(self.controller.set_operator_role("admin", password="wrong"))
        self.assertEqual(self.controller.get_operator_role(), current_role)

        self.assertTrue(self.controller.set_operator_role("admin", password="admin123"))
        self.assertEqual(self.controller.get_operator_role(), "admin")

    def test_technician_role_requires_correct_password(self) -> None:
        self.controller.set_operator_role("user")
        current_role = self.controller.get_operator_role()
        self.assertFalse(self.controller.set_operator_role("technician", password="bad"))
        self.assertEqual(self.controller.get_operator_role(), current_role)

        self.assertTrue(self.controller.set_operator_role("technician", password="tech123"))
        self.assertEqual(self.controller.get_operator_role(), "technician")


if __name__ == "__main__":
    unittest.main()
