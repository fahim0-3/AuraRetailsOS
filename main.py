# ============================================================
# Subsystem: Main  Role: Entry point — 3 simulation scenarios
# ============================================================

from __future__ import annotations
import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from factories.pharmacy_kiosk_factory import PharmacyKioskFactory
from factories.food_kiosk_factory import FoodKioskFactory
from factories.emergency_relief_factory import EmergencyReliefKioskFactory
from hardware.refrigeration_module import RefrigerationModule
from hardware.solar_monitor_module import SolarMonitorModule
from hardware.base_kiosk import BaseKiosk
from hardware.spiral_dispenser import SpiralDispenserImpl
from hardware.conveyor_dispenser import ConveyorDispenserImpl
from core.kiosk_interface import KioskInterface
from inventory.product import Product
from inventory.product_bundle import ProductBundle
from inventory.inventory_proxy import InventoryProxy
from payment.credit_card_adapter import CreditCardAdapter
from core.central_registry import CentralRegistry


def scenario_1() -> None:
    """Scenario 1: Hardware Module Attachment (Decorator + Bridge)"""
    print("\n" + "=" * 60)
    print("=== SCENARIO 1: Adding Optional Hardware Modules ===")
    print("=" * 60)

    print("\nStep 1: Create PharmacyKiosk via PharmacyKioskFactory")
    kiosk = KioskInterface(PharmacyKioskFactory(), "KIOSK-001")

    print("\nStep 2: Run diagnostics (base + RoboticArm dispenser)")
    kiosk.run_diagnostics()

    print("\nStep 3: Attach RefrigerationModule and run diagnostics")
    kiosk.attach_module(RefrigerationModule(kiosk._module_chain))
    kiosk.run_diagnostics()

    print("\nStep 4: Attach SolarMonitorModule and run diagnostics")
    kiosk.attach_module(SolarMonitorModule(kiosk._module_chain))
    kiosk.run_diagnostics()

    print("\nStep 5: Swap dispenser to SpiralDispenserImpl (Bridge hot-swap)")
    kiosk.swap_dispenser(SpiralDispenserImpl())

    print("\nStep 6: Run diagnostics again (Spiral dispenser, modules still chained)")
    kiosk.run_diagnostics()
    print()


def scenario_2() -> None:
    """Scenario 2: Payment Provider Integration (Adapter + Command)"""
    print("\n" + "=" * 60)
    print("=== SCENARIO 2: Multi-Provider Payment Integration ===")
    print("=" * 60)

    print("\nStep 1: Create FoodKiosk (uses UPI by default)")
    kiosk = KioskInterface(FoodKioskFactory(), "KIOSK-002")

    print("\nStep 2: Add product Sandwich (FOOD-001, price=80, stock=10) to inventory")
    sandwich = Product("FOOD-001", "Sandwich", 80.0, total_stock=10)
    kiosk.add_product(sandwich)
    print("  Added: Sandwich (FOOD-001) — stock: 10")

    print("\nStep 3: Purchase FOOD-001 via UPI")
    result = kiosk.purchase_item("FOOD-001", "USER-001", 1)
    print(f"  Purchase result: {'SUCCESS' if result else 'FAILED'}")

    print("\nStep 4: Print transaction history")
    kiosk.print_transaction_history()

    print("\nStep 5: Swap payment to CreditCardAdapter")
    kiosk.payment = CreditCardAdapter()
    print("  Payment provider swapped to CreditCard")

    print("\nStep 6: Purchase FOOD-001 via CreditCard")
    result = kiosk.purchase_item("FOOD-001", "USER-002", 1)
    print(f"  Purchase result: {'SUCCESS' if result else 'FAILED'}")

    print("\nStep 7: RefundTransaction on last purchase")
    kiosk.refund_transaction("TX-REFUND-001", 80.0)
    print("  Refund issued")

    print("\nStep 8: Print transaction history (shows all transactions)")
    kiosk.print_transaction_history()
    print()


def scenario_3() -> None:
    """Scenario 3: Nested Bundle Inventory (Composite + Proxy)"""
    print("\n" + "=" * 60)
    print("=== SCENARIO 3: Nested Product Bundle Availability ===")
    print("=" * 60)

    print("\nStep 1: Create EmergencyReliefKiosk")
    kiosk = KioskInterface(EmergencyReliefKioskFactory(), "KIOSK-003")

    print("\nStep 2: Add products: Bandage(stock=5), Antiseptic(stock=3), Painkiller(stock=10)")
    bandage = Product("MED-B001", "Bandage", 15.0, total_stock=5)
    antiseptic = Product("MED-B002", "Antiseptic", 30.0, total_stock=3)
    painkiller = Product("MED-B003", "Painkiller", 20.0, total_stock=10)
    kiosk.add_product(bandage)
    kiosk.add_product(antiseptic)
    kiosk.add_product(painkiller)
    print("  Added: Bandage (MED-B001), Antiseptic (MED-B002), Painkiller (MED-B003)")

    print("\nStep 3: Create FirstAidKit bundle (Bandage + Antiseptic)")
    first_aid_kit = ProductBundle("KIT-001", "FirstAidKit")
    first_aid_kit.add_item(bandage)
    first_aid_kit.add_item(antiseptic)
    kiosk.add_product(first_aid_kit)

    print("\nStep 4: Create EmergencyKit bundle (FirstAidKit + Painkiller)")
    emergency_kit = ProductBundle("KIT-002", "EmergencyKit")
    emergency_kit.add_item(first_aid_kit)
    emergency_kit.add_item(painkiller)
    kiosk.add_product(emergency_kit)

    print("\nStep 5: Display inventory (full tree)")
    print()
    kiosk.display_inventory()

    print("\nStep 6: Purchase EmergencyKit (USER-001) — should SUCCESS")
    result = kiosk.purchase_item("KIT-002", "USER-001", 1)
    print(f"  Purchase result: {'SUCCESS' if result else 'FAILED'}")

    print("\nStep 7: Display inventory (reduced stock)")
    print()
    kiosk.display_inventory()

    print("\nStep 8: Set Bandage hardware_available=false (hardware fault)")
    bandage.set_hardware_available(False)
    print("  Bandage hardware set to FAULT")

    print("\nStep 9: Purchase EmergencyKit again — should FAIL (Bandage unavailable)")
    result = kiosk.purchase_item("KIT-002", "USER-001", 1)
    print(f"  Purchase result: {'SUCCESS' if result else 'FAILED'}")

    print("\nStep 10: Attempt unauthorized update_stock as 'user' role")
    user_proxy = InventoryProxy("user")
    result = user_proxy.update_stock("KIT-002", 5)
    print(f"  Unauthorized update result: {'SUCCESS' if result else 'BLOCKED (expected)'}")

    print("\nStep 11: Restore hardware — purchase EmergencyKit — should SUCCESS again")
    bandage.set_hardware_available(True)
    print("  Bandage hardware restored to OK")
    result = kiosk.purchase_item("KIT-002", "USER-001", 1)
    print(f"  Purchase result: {'SUCCESS' if result else 'FAILED'}")
    print()


def main() -> None:
    CentralRegistry.get_instance().log_event("=== AuraRetailOS Starting ===")

    scenario_1()
    scenario_2()
    scenario_3()

    CentralRegistry.get_instance().log_event("=== AuraRetailOS Complete ===")

    print("=" * 60)
    print("All scenarios complete. Check transaction logs above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
