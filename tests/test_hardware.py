# ============================================================
# Subsystem: Tests  Pattern: Testing  Role: Test hardware functionality
# ============================================================

import unittest
from hardware.spiral_dispenser import SpiralDispenserImpl
from hardware.conveyor_dispenser import ConveyorDispenserImpl
from hardware.robotic_arm_dispenser import RoboticArmDispenserImpl
from hardware.dispenser_controller import DispenserController
from hardware.base_kiosk import BaseKiosk
from hardware.refrigeration_module import RefrigerationModule
from hardware.solar_monitor_module import SolarMonitorModule
from hardware.network_module import NetworkModule
from hardware.i_kiosk_module import IKioskModule


class TestHardware(unittest.TestCase):
    def test_dispenser_implementations(self):
        spiral = SpiralDispenserImpl()
        conveyor = ConveyorDispenserImpl()
        robotic = RoboticArmDispenserImpl()

        self.assertTrue(spiral.dispense_item("TEST", 1))
        self.assertTrue(spiral.self_test())
        self.assertEqual(spiral.get_hardware_type(), "SpiralDispenser")

        self.assertTrue(conveyor.dispense_item("TEST", 1))
        self.assertTrue(conveyor.self_test())
        self.assertEqual(conveyor.get_hardware_type(), "ConveyorDispenser")

        self.assertTrue(robotic.dispense_item("TEST", 1))
        self.assertTrue(robotic.self_test())
        self.assertEqual(robotic.get_hardware_type(), "RoboticArmDispenser")

    def test_dispenser_controller_bridge(self):
        spiral = SpiralDispenserImpl()
        conveyor = ConveyorDispenserImpl()
        controller = DispenserController(spiral)

        self.assertEqual(controller.current_hardware_type, "SpiralDispenser")
        self.assertTrue(controller.dispense("TEST", 1))
        self.assertTrue(controller.run_self_test())

        # Test hot-swap
        controller.set_impl(conveyor)
        self.assertEqual(controller.current_hardware_type, "ConveyorDispenser")
        self.assertTrue(controller.dispense("TEST", 1))
        self.assertTrue(controller.run_self_test())

    def test_kiosk_modules_decorator(self):
        base = BaseKiosk()
        self.assertEqual(base.get_module_info(), "[BaseKiosk] operational")
        self.assertTrue(base.is_operational())

        # Test refrigeration decorator
        refrigerated = RefrigerationModule(base)
        self.assertIn("[BaseKiosk] operational", refrigerated.get_module_info())
        self.assertIn("[Refrigeration] active, temp: -4C", refrigerated.get_module_info())
        self.assertTrue(refrigerated.is_operational())

        # Test solar monitor decorator
        solar_refrigerated = SolarMonitorModule(refrigerated)
        self.assertIn("[BaseKiosk] operational", solar_refrigerated.get_module_info())
        self.assertIn("[Refrigeration] active, temp: -4C", solar_refrigerated.get_module_info())
        self.assertIn("[Solar] output: 220W", solar_refrigerated.get_module_info())
        self.assertTrue(solar_refrigerated.is_operational())

        # Test network module
        network_solar_refrigerated = NetworkModule(solar_refrigerated)
        self.assertIn("[BaseKiosk] operational", network_solar_refrigerated.get_module_info())
        self.assertIn("[Refrigeration] active, temp: -4C", network_solar_refrigerated.get_module_info())
        self.assertIn("[Solar] output: 220W", network_solar_refrigerated.get_module_info())
        self.assertIn("[Network] signal: strong", network_solar_refrigerated.get_module_info())
        self.assertTrue(network_solar_refrigerated.is_operational())

    def test_module_operational_chain(self):
        base = BaseKiosk()
        # If base is operational, all decorations should be operational
        refrigerated = RefrigerationModule(base)
        solar_refrigerated = SolarMonitorModule(refrigerated)
        network_solar_refrigerated = NetworkModule(solar_refrigerated)

        self.assertTrue(base.is_operational())
        self.assertTrue(refrigerated.is_operational())
        self.assertTrue(solar_refrigerated.is_operational())
        self.assertTrue(network_solar_refrigerated.is_operational())

        # If we make base non-operational, chain should reflect that
        # Note: BaseKiosk.is_operational() always returns True in current implementation
        # This test validates the delegation pattern works


if __name__ == '__main__':
    unittest.main()