# 🛒 Aura Retail OS — Path B: Modular Hardware Platform

> A modular, extensible retail kiosk simulation built with Python 3.10+, demonstrating nine
> Gang-of-Four design patterns through a real-world retail operations domain.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Path B Objectives](#path-b-objectives)
4. [Implemented Features](#implemented-features)
5. [Hardware Abstraction Layer](#hardware-abstraction-layer)
6. [Optional Hardware Modules](#optional-hardware-modules)
7. [Payment Provider Integration](#payment-provider-integration)
8. [Inventory Hierarchy (Composite)](#inventory-hierarchy-composite)
9. [System Architecture](#system-architecture)
10. [OOP Principles Demonstrated](#oop-principles-demonstrated)
11. [Design Patterns Implemented](#design-patterns-implemented)
12. [Folder Structure](#folder-structure)
13. [Setup & Run Instructions](#setup--run-instructions)
14. [Demo / Simulation Scenarios](#demo--simulation-scenarios)
15. [Desktop GUI (PySide6)](#desktop-gui-pyside6)
16. [Persistence](#persistence)
17. [Testing](#testing)
18. [Known Limitations](#known-limitations)
19. [Future Enhancements](#future-enhancements)

---

## Project Overview

**Aura Retail OS** is a retail kiosk simulation with both console scenarios and a PySide6
desktop GUI. The project models a complete kiosk lifecycle—hardware configuration,
inventory management, payment processing, and transactional operations—entirely through
object-oriented design patterns.

The system supports multiple kiosk variants (Pharmacy, Food, Emergency Relief), each
assembled via an Abstract Factory that wires together the correct dispenser hardware,
payment provider, and inventory manager. Optional hardware modules (Refrigeration, Solar
Monitor, Network) can be attached at runtime using the Decorator pattern, and the dispenser
mechanism can be hot-swapped without a system restart via the Bridge pattern.

All transactions (purchase, refund, restock) are encapsulated as Command objects, recorded
in an invoker history, and support full undo/rollback semantics with stock reservation
safety.

---

## Problem Statement

Modern retail kiosk deployments face several challenges:

- **Hardware diversity** — Different deployment contexts require different dispenser
  mechanisms (spiral vending, conveyor belt, robotic arm) and auxiliary modules
  (refrigeration, solar power monitoring, network connectivity).
- **Payment fragmentation** — Kiosks must integrate with multiple, often incompatible,
  third-party payment gateways (credit card, UPI, digital wallets) without coupling
  business logic to any single vendor.
- **Inventory complexity** — Products may be sold individually or as nested bundles
  (e.g., a FirstAidKit containing a Bandage and Antiseptic, nested inside a larger
  EmergencyKit), requiring recursive availability checks and stock calculations.
- **Access control** — Stock modifications must be restricted by role (admin, technician,
  user) to prevent unauthorized restocking or inventory manipulation.
- **Transactional safety** — Purchases involve a multi-step pipeline (availability check →
  stock reservation → payment → dispensing → finalization) where any step can fail,
  requiring automatic rollback of all preceding steps.

---

## Path B Objectives

Path B focuses on building a **Modular Hardware Platform** with the following goals:

1. **Implement nine GoF design patterns** (Singleton, Abstract Factory, Bridge, Decorator,
   Adapter, Composite, Proxy, Command, Facade) cohesively in a single domain.
2. **Model a pluggable hardware layer** where dispenser implementations can be swapped at
   runtime without modifying client code.
3. **Support optional hardware modules** that can be dynamically attached via decorator
   chaining.
4. **Integrate multiple incompatible payment APIs** through a uniform adapter interface.
5. **Represent inventory as a tree structure** supporting individual products and recursive
   bundles.
6. **Enforce role-based access control** on inventory mutations via a protection proxy.
7. **Encapsulate all state-changing operations** as undoable command objects with full
   transaction history.
8. **Provide a unified facade** that hides subsystem complexity from client code.
9. **Maintain a global singleton registry** for system-wide configuration and event logging.

---

## Implemented Features

| Feature | Status | Key Classes |
|---|:---:|---|
| Multi-variant kiosk assembly | ✓ | `PharmacyKioskFactory`, `FoodKioskFactory`, `EmergencyReliefKioskFactory` |
| Runtime dispenser hot-swap | ✓ | `DispenserController`, `IDispenserImpl` |
| Decorator module chaining | ✓ | `RefrigerationModule`, `SolarMonitorModule`, `NetworkModule` |
| Multi-provider payments | ✓ | `CreditCardAdapter`, `UPIAdapter`, `DigitalWalletAdapter` |
| Nested product bundles | ✓ | `Product`, `ProductBundle`, `IInventoryItem` |
| Role-based inventory proxy | ✓ | `InventoryProxy` (admin / technician / user) |
| Transactional purchase pipeline | ✓ | `PurchaseItemCommand` (reserve → pay → dispense → finalize) |
| Auto-rollback on failure | ✓ | Stock release + payment refund on pipeline failure |
| Undo/Redo support | ✓ | `CommandInvoker.undo_last()` |
| Refund processing | ✓ | `RefundCommand` |
| Inventory restocking | ✓ | `RestockCommand` |
| Hardware fault simulation | ✓ | `Product.set_hardware_available()` |
| JSON persistence (inventory) | ✓ | `InventoryManager.load_from_file()` / `save_to_file()` |
| JSON persistence (transactions) | ✓ | `CommandInvoker.persist_history()` |
| JSON persistence (config) | ✓ | `CentralRegistry.load_config()` / `save_config()` |
| System-wide event logging | ✓ | `CentralRegistry.log_event()` |
| Kiosk diagnostics | ✓ | `KioskInterface.run_diagnostics()` |
| Pricing policy subsystem | ✓ | `IPricingPolicy`, `StandardPricingPolicy`, `DiscountPricingPolicy`, `EmergencyPricingPolicy` |
| Emergency-mode purchase constraints | ✓ | `KioskVerificationModule`, `maxPurchasePerUser` + essential-item checks |
| Operational purchase gating (hardware/mode/network) | ✓ | `BaseKiosk.is_operational()`, `NetworkModule.is_operational()`, `KioskInterface.purchase_item()` verification context |
| Hardware dependency mapping | ✓ | `Product.required_modules`, runtime module verification before purchase |
| Factory pricing/verification modules | ✓ | `AbstractKioskFactory.create_pricing_policy()` / `create_verification_module()` |
| Desktop GUI (PySide6) | ✓ | `gui/`, `KioskController`, `run_gui.py` |
| Unit test suite | ✓ | `tests/` (hardware, inventory, payment, transactions) |

---

## Hardware Abstraction Layer

The **Bridge pattern** decouples the dispenser abstraction from its concrete hardware
implementation, enabling runtime hot-swap without restarting the kiosk.

```
DispenserController (Abstraction)
   │
   ├── set_impl(new_impl)   ← hot-swap at runtime
   ├── dispense(product_id, qty)
   └── run_self_test()
         │
         ▼
   IDispenserImpl (Implementor Interface)
         │
         ├── SpiralDispenserImpl     — rotating spiral mechanism
         ├── ConveyorDispenserImpl   — belt-drive with photocell sensor
         └── RoboticArmDispenserImpl — 6-DOF pick-and-place arm
```

**Hot-swap example** (from Scenario 1):

```python
kiosk.swap_dispenser(SpiralDispenserImpl())
# Output: [BRIDGE] Dispenser hot-swapped to: SpiralDispenser — no system restart required
```

---

## Optional Hardware Modules

The **Decorator pattern** allows optional hardware modules to be attached to a kiosk
at runtime. Each decorator wraps the existing module chain, adding its own behavior
while delegating to the wrapped module.

```
IKioskModule (Component Interface)
   │
   ├── BaseKiosk (Concrete Component — always present)
   │
   └── KioskModuleDecorator (Abstract Decorator)
          │
          ├── RefrigerationModule   — temperature monitoring (-4°C)
          ├── SolarMonitorModule    — solar power output (220W)
          └── NetworkModule         — network signal strength
```

**Chaining example** (from Scenario 1):

```python
kiosk.attach_module(RefrigerationModule(kiosk._module_chain))
kiosk.attach_module(SolarMonitorModule(kiosk._module_chain))
# Diagnostics now print: BaseKiosk → RefrigerationModule → SolarMonitorModule
```

Each module's `perform_check()` delegates to the wrapped module first, then prints its
own status, producing a full diagnostic chain.

---

## Payment Provider Integration

The **Adapter pattern** integrates three incompatible legacy payment APIs behind a
uniform `IPaymentProcessor` interface.

| Legacy API | Incompatibility | Adapter |
|---|---|---|
| `LegacyCreditCardGateway` | Uses `authorize(amt, card_token)` / `reverse_charge(txn_ref)` | `CreditCardAdapter` |
| `LegacyDigitalWalletAPI` | Returns `int` (0 = success) instead of `bool`; `initiate_refund()` returns `None` | `DigitalWalletAdapter` |
| `LegacyUPISystem` | Uses `send_upi_request(vpa, rupees)` / `raise_dispute(upi_ref)` | `UPIAdapter` |

All adapters expose the same interface:

```python
class IPaymentProcessor(ABC):
    def process_payment(self, amount: float, user_id: str) -> bool: ...
    def refund_payment(self, transaction_id: str, amount: float) -> bool: ...
    def get_provider_name(self) -> str: ...
```

Payment providers can be swapped at runtime:

```python
kiosk.payment = CreditCardAdapter()  # swap from UPI to CreditCard
```

---

## Inventory Hierarchy (Composite)

The **Composite pattern** models products and product bundles as a uniform tree structure.

```
IInventoryItem (Component Interface)
   │
   ├── Product (Leaf)
   │     ├── item_id, name, price
   │     ├── total_stock, reserved_stock
   │     ├── hardware_available flag
   │     ├── get_available_stock() → total - reserved
   │     └── is_available() → stock > 0 AND hardware OK
   │
   └── ProductBundle (Composite)
         ├── _children: list[IInventoryItem]
         ├── price → sum of children's prices (recursive)
         ├── get_available_stock() → min of children's stock (recursive)
         └── is_available() → all children available (recursive)
```

**Nested bundle example** (from Scenario 3):

```
[BUNDLE] EmergencyKit (KIT-002) — $65.00 — stock: 3
   [BUNDLE] FirstAidKit (KIT-001) — $45.00 — stock: 3
      [PRODUCT] Bandage (MED-B001) — $15.00 — stock: 5
      [PRODUCT] Antiseptic (MED-B002) — $30.00 — stock: 3
   [PRODUCT] Painkiller (MED-B003) — $20.00 — stock: 10
```

A bundle is available only if **all** its children (recursively) are available. Its
effective stock is the **minimum** stock across all leaf children.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        main.py                               │
│            (3 simulation scenarios)                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  KioskInterface (FACADE)                      │
│  purchase_item() │ refund_transaction() │ restock_inventory() │
│  run_diagnostics() │ display_inventory() │ swap_dispenser()   │
│  attach_module() │ print_transaction_history()                │
└───┬──────────┬───────────┬───────────┬───────────┬───────────┘
    │          │           │           │           │
    ▼          ▼           ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐
│Abstract│ │Bridge  │ │Decorator│ │Adapter  │ │Command      │
│Factory │ │Layer   │ │Chain    │ │Layer    │ │Invoker      │
│        │ │        │ │         │ │         │ │             │
│Pharmacy│ │Dispens.│ │Base     │ │Credit   │ │Purchase     │
│Food    │ │Control.│ │+Refrig. │ │Card     │ │Refund       │
│Emerg.  │ │        │ │+Solar   │ │UPI      │ │Restock      │
│Relief  │ │Spiral  │ │+Network │ │Digital  │ │             │
│        │ │Conveyor│ │         │ │Wallet   │ │History +    │
│        │ │Robotic │ │         │ │         │ │Undo support │
└────────┘ └────────┘ └─────────┘ └─────────┘ └─────────────┘
    │                                               │
    ▼                                               ▼
┌──────────────────────────────────────┐  ┌─────────────────┐
│ Inventory Subsystem                  │  │ CentralRegistry  │
│                                      │  │ (SINGLETON)      │
│ InventoryProxy (PROXY)               │  │                  │
│   └─► InventoryManager (Real)        │  │ Event log        │
│         └─► Product (Leaf)           │  │ Status map       │
│         └─► ProductBundle (Composite)│  │ Config I/O       │
└──────────────────────────────────────┘  └─────────────────┘
```

---

## OOP Principles Demonstrated

### Encapsulation

- `Product` encapsulates stock state (`_total_stock`, `_reserved_stock`,
  `_hardware_available`) as private attributes, exposed only through controlled methods
  (`reserve()`, `release()`, `deduct()`, `restock()`).
- `CentralRegistry` encapsulates `_status_map` and `_event_log` behind accessor methods.

### Abstraction

- `IDispenserImpl`, `IPaymentProcessor`, `IKioskModule`, `IInventoryItem`, and
  `IInventoryManager` are pure abstract interfaces (using `ABC` + `@abstractmethod`) that
  hide implementation details from consumers.
- `KioskInterface` acts as a high-level abstraction over five subsystems.

### Inheritance

- `KioskModuleDecorator` inherits from `IKioskModule` and serves as the abstract base for
  all concrete decorator modules (`RefrigerationModule`, `SolarMonitorModule`,
  `NetworkModule`).
- All three concrete factories inherit from `AbstractKioskFactory`.
- All three concrete dispenser implementations inherit from `IDispenserImpl`.
- All three payment adapters inherit from `IPaymentProcessor`.
- All three concrete commands inherit from `ICommand`.

### Polymorphism

- `KioskInterface` operates on `IDispenserImpl`, `IPaymentProcessor`, and
  `IInventoryManager` interfaces—any concrete implementation can be substituted at runtime.
- `IInventoryItem.display()` is polymorphically dispatched: `Product` prints a leaf node,
  `ProductBundle` prints itself then recursively calls `display()` on its children.
- The `CommandInvoker` treats all commands uniformly via the `ICommand` interface.

---

## Design Patterns Implemented

### 1. Singleton — `CentralRegistry`

**File:** `core/central_registry.py`

**Purpose:** Ensures a single, globally accessible instance for system-wide event logging,
status tracking, and configuration persistence.

**Implementation:** Overrides `__new__()` to guard instance creation. A static
`get_instance()` method provides convenient access.

```python
class CentralRegistry:
    _instance = None

    def __new__(cls) -> CentralRegistry:
        if CentralRegistry._instance is None:
            CentralRegistry._instance = super().__new__(cls)
            CentralRegistry._instance._status_map = {}
            CentralRegistry._instance._event_log = []
        return CentralRegistry._instance
```

**Usage:** Every command (`PurchaseItemCommand`, `RefundCommand`, `RestockCommand`) and the
`InventoryProxy` log events to the shared registry.

---

### 2. Abstract Factory — `AbstractKioskFactory` + Concrete Factories

**Files:**
- `core/abstract_kiosk_factory.py` — abstract interface
- `factories/pharmacy_kiosk_factory.py` — `PharmacyKioskFactory`
- `factories/food_kiosk_factory.py` — `FoodKioskFactory`
- `factories/emergency_relief_factory.py` — `EmergencyReliefKioskFactory`

**Purpose:** Encapsulates the creation of a family of related objects (dispenser, payment
processor, inventory manager) without specifying their concrete classes.

| Factory | Dispenser | Payment | Inventory Role |
|---|---|---|---|
| `PharmacyKioskFactory` | `RoboticArmDispenserImpl` | `CreditCardAdapter` | admin |
| `FoodKioskFactory` | `ConveyorDispenserImpl` | `UPIAdapter` | user |
| `EmergencyReliefKioskFactory` | `SpiralDispenserImpl` | `DigitalWalletAdapter` | technician |

**Usage:** The `KioskInterface` constructor accepts any `AbstractKioskFactory` and delegates
object creation to it, achieving complete decoupling from concrete product classes.

---

### 3. Bridge — `DispenserController` / `IDispenserImpl`

**Files:**
- `hardware/dispenser_controller.py` — abstraction
- `hardware/i_dispenser.py` — implementor interface
- `hardware/spiral_dispenser.py` — `SpiralDispenserImpl`
- `hardware/conveyor_dispenser.py` — `ConveyorDispenserImpl`
- `hardware/robotic_arm_dispenser.py` — `RoboticArmDispenserImpl`

**Purpose:** Separates the dispenser abstraction (control logic) from its hardware
implementation (physical mechanism), allowing both to vary independently. Supports
runtime hot-swap via `set_impl()`.

**Usage:** Scenario 1 demonstrates hot-swapping from `RoboticArmDispenserImpl` to
`SpiralDispenserImpl` mid-session without system restart.

---

### 4. Decorator — `KioskModuleDecorator` + Concrete Modules

**Files:**
- `hardware/i_kiosk_module.py` — component interface
- `hardware/base_kiosk.py` — concrete component
- `hardware/kiosk_module_decorator.py` — abstract decorator
- `hardware/refrigeration_module.py` — `RefrigerationModule`
- `hardware/solar_monitor_module.py` — `SolarMonitorModule`
- `hardware/network_module.py` — `NetworkModule`

**Purpose:** Dynamically adds optional hardware capabilities to a kiosk without modifying
its class. Each decorator wraps the existing module chain, delegating `perform_check()`
and `get_module_info()` to the wrapped module before appending its own behavior.

**Usage:** Scenario 1 attaches Refrigeration and Solar Monitor modules to a PharmacyKiosk,
and diagnostics reflect the full decorator chain.

---

### 5. Adapter — Payment Adapters

**Files:**
- `payment/i_payment_processor.py` — target interface
- `payment/legacy_stubs.py` — simulated incompatible third-party APIs
- `payment/credit_card_adapter.py` — `CreditCardAdapter`
- `payment/digital_wallet_adapter.py` — `DigitalWalletAdapter`
- `payment/upi_adapter.py` — `UPIAdapter`

**Purpose:** Converts the interface of incompatible legacy payment APIs into the uniform
`IPaymentProcessor` interface expected by the kiosk system. Each adapter wraps a legacy
API object and translates method calls and return types.

**Usage:** Scenario 2 demonstrates purchasing via UPI, then swapping to CreditCard
mid-session and purchasing again.

---

### 6. Composite — `IInventoryItem` / `Product` / `ProductBundle`

**Files:**
- `inventory/i_inventory_item.py` — component interface
- `inventory/product.py` — leaf node
- `inventory/product_bundle.py` — composite node

**Purpose:** Represents individual products and nested product bundles as a uniform tree
structure. Bundles recursively aggregate their children's prices (sum), availability
(all), and effective stock (min).

**Usage:** Scenario 3 creates a nested hierarchy: `EmergencyKit` → contains `FirstAidKit`
(→ contains `Bandage` + `Antiseptic`) + `Painkiller`. Purchasing the top-level bundle
recursively deducts stock from all leaf products.

---

### 7. Proxy — `InventoryProxy`

**Files:**
- `inventory/i_inventory_manager.py` — subject interface
- `inventory/inventory_manager.py` — real subject
- `inventory/inventory_proxy.py` — protection proxy

**Purpose:** Controls access to the real `InventoryManager` by enforcing role-based
authorization. The proxy intercepts `add_item()`, `update_stock()`, `restock()`, and
`deduct_total_stock()` and blocks unauthorized operations based on the caller's role.

| Operation | admin | technician | user |
|---|:---:|:---:|:---:|
| `add_item()` | ✓ | ✗   | ✗   |
| `update_stock()` (positive / restock) | ✓ | ✓ | ✗   |
| `update_stock()` (negative / reserve) | ✓ | ✓ | ✓ |
| `restock()` | ✓ | ✓ | ✗   |
| `deduct_total_stock()` | ✓ | ✓ | ✗   |
| `finalize_purchase()` | ✓ | ✓ | ✓ |
| `get_item()` / `list_all()` | ✓ | ✓ | ✓ |

**Usage:** Scenario 3 demonstrates a `user`-role proxy being blocked from calling
`update_stock()` with a positive delta.

---

### 8. Command — `ICommand` + Concrete Commands

**Files:**
- `transaction/i_command.py` — command interface
- `transaction/purchase_item_command.py` — `PurchaseItemCommand`
- `transaction/refund_command.py` — `RefundCommand`
- `transaction/restock_command.py` — `RestockCommand`
- `transaction/command_invoker.py` — `CommandInvoker`

**Purpose:** Encapsulates each transactional operation as a self-contained object with
`execute()` and `undo()` methods. The `CommandInvoker` maintains a full history and
supports undo.

#### PurchaseItemCommand pipeline:

```
1. Check item availability + hardware status
2. Reserve stock (update_stock with negative delta)
3. Process payment via adapter
4. Dispense item via bridge controller
5. Finalize purchase (deduct total stock, release reservation)
```

If any step fails, all preceding steps are automatically rolled back:
- Payment failure → release reserved stock
- Dispense failure → refund payment + release reserved stock

**Usage:** Scenarios 2 and 3 execute purchases; Scenario 2 also issues a refund.

---

### 9. Facade — `KioskInterface`

**File:** `core/kiosk_interface.py`

**Purpose:** Provides a single, simplified entry point for all kiosk interactions, hiding
the complexity of the underlying subsystems (inventory, payment, dispensing, modules,
transaction history).

**Exposed API:**

| Method | Delegates To |
|---|---|
| `purchase_item()` | Inventory + Payment + Dispenser via `PurchaseItemCommand` |
| `refund_transaction()` | Payment via `RefundCommand` |
| `restock_inventory()` | Inventory via `RestockCommand` |
| `run_diagnostics()` | Dispenser + Module chain |
| `display_inventory()` | `InventoryManager.list_all()` |
| `swap_dispenser()` | `DispenserController.set_impl()` |
| `attach_module()` | Decorator chain |
| `print_transaction_history()` | `CommandInvoker.print_history()` |
| `add_product()` | `InventoryManager.add_item()` (bypasses proxy for setup) |

**Usage:** `main.py` interacts exclusively through `KioskInterface` — no direct subsystem
access is needed.

---

## Folder Structure

```
AuraRetailOS/
│
├── main.py                          # Entry point — runs 3 simulation scenarios
├── run_gui.py                       # PySide6 entry point
│
├── core/                            # Core system infrastructure
│   ├── __init__.py
│   ├── central_registry.py          # Singleton — event log, status map, config I/O
│   ├── abstract_kiosk_factory.py    # Abstract Factory interface
│   └── kiosk_interface.py           # Facade — unified kiosk API
│
├── gui/                             # PySide6 desktop frontend
│   ├── __init__.py
│   ├── app.py                       # QApplication bootstrap + styling
│   ├── kiosk_controller.py          # QObject bridge to KioskInterface facade
│   ├── main_window.py               # Main window + tab container
│   └── tabs/
│       ├── __init__.py
│       ├── hardware_tab.py          # Scenario 1 controls (modules/dispenser/diagnostics)
│       ├── inventory_tab.py         # Inventory tree + JSON load/save + add product/bundle
│       ├── transactions_tab.py      # Purchase/refund/payment swap controls
│       └── history_tab.py           # Command history table + CentralRegistry event log
│
├── factories/                       # Concrete Abstract Factory implementations
│   ├── __init__.py
│   ├── pharmacy_kiosk_factory.py    # Pharmacy variant (RoboticArm + CreditCard)
│   ├── food_kiosk_factory.py        # Food variant (Conveyor + UPI)
│   └── emergency_relief_factory.py  # Emergency variant (Spiral + DigitalWallet)
│
├── hardware/                        # Hardware abstraction (Bridge + Decorator)
│   ├── __init__.py
│   ├── i_dispenser.py               # Bridge — implementor interface
│   ├── dispenser_controller.py      # Bridge — abstraction (hot-swap controller)
│   ├── spiral_dispenser.py          # Bridge — spiral mechanism implementor
│   ├── conveyor_dispenser.py        # Bridge — conveyor belt implementor
│   ├── robotic_arm_dispenser.py     # Bridge — robotic arm implementor
│   ├── i_kiosk_module.py            # Decorator — component interface
│   ├── base_kiosk.py                # Decorator — base concrete component
│   ├── kiosk_module_decorator.py    # Decorator — abstract decorator
│   ├── refrigeration_module.py      # Decorator — refrigeration add-on
│   ├── solar_monitor_module.py      # Decorator — solar monitoring add-on
│   └── network_module.py            # Decorator — network connectivity add-on
│
├── inventory/                       # Inventory management (Composite + Proxy)
│   ├── __init__.py
│   ├── i_inventory_item.py          # Composite — component interface
│   ├── product.py                   # Composite — leaf (individual product)
│   ├── product_bundle.py            # Composite — composite (nested bundle)
│   ├── i_inventory_manager.py       # Proxy — subject interface
│   ├── inventory_manager.py         # Proxy — real subject (manages items + JSON I/O)
│   └── inventory_proxy.py           # Proxy — protection proxy (role-based access)
│
├── payment/                         # Payment integration (Adapter)
│   ├── __init__.py
│   ├── i_payment_processor.py       # Adapter — target interface
│   ├── legacy_stubs.py              # Adapter — simulated incompatible legacy APIs
│   ├── credit_card_adapter.py       # Adapter — wraps LegacyCreditCardGateway
│   ├── digital_wallet_adapter.py    # Adapter — wraps LegacyDigitalWalletAPI
│   └── upi_adapter.py              # Adapter — wraps LegacyUPISystem
│
├── transaction/                     # Transaction processing (Command)
│   ├── __init__.py
│   ├── i_command.py                 # Command — interface (execute + undo)
│   ├── purchase_item_command.py     # Command — purchase with 5-step pipeline
│   ├── refund_command.py            # Command — refund processing
│   ├── restock_command.py           # Command — inventory restocking
│   └── command_invoker.py           # Command — invoker with history + persistence
│
├── tests/                           # Unit test suite
│   ├── __init__.py
│   ├── test_hardware.py             # Tests Bridge + Decorator patterns
│   ├── test_inventory.py            # Tests Composite + Proxy patterns
│   ├── test_payment.py              # Tests Adapter pattern + legacy stubs
│   └── test_transactions.py         # Tests Command pattern + rollback/undo
│
├── data/                            # JSON persistence files
│   ├── config.json                  # Kiosk configuration (id, type, payment provider)
│   ├── inventory.json               # Seed inventory data (products + bundles)
│   └── transactions.json            # Transaction history output
│
├── test_output.txt                  # Captured test run output
└── test_errors.txt                  # Captured test error output
```

**Total:** 45+ source files across 8 packages, plus 3 JSON data files.

---

## Setup & Run Instructions

### Prerequisites

- **Python 3.10+** (uses `match` statement–free code, `from __future__ import annotations`,
  type hints with `X | Y` union syntax)
- **PySide6** for the desktop GUI (`pip install PySide6`)
- Core simulation logic uses only standard library modules (`abc`, `json`, `uuid`,
  `datetime`, `unittest`, `unittest.mock`)

### Installation

```bash
# Clone or download the project
cd AuraRetailOS

# Install GUI dependency
pip install PySide6
```

### Running the Console Simulation

```bash
python main.py
```

This executes all three simulation scenarios sequentially and prints detailed console
output for each step.

### Running the GUI

```bash
python run_gui.py
```

Optional startup flags:

```bash
python run_gui.py --kiosk-type pharmacy --kiosk-id KIOSK-001
python run_gui.py --kiosk-type food --kiosk-id KIOSK-002
python run_gui.py --kiosk-type emergency --kiosk-id KIOSK-003
```

### Running the Tests

```bash
# Run all tests
python -m unittest discover -s tests -v

# Run individual test modules
python -m unittest tests.test_hardware -v
python -m unittest tests.test_inventory -v
python -m unittest tests.test_payment -v
python -m unittest tests.test_transactions -v
```

---

## Demo / Simulation Scenarios

`main.py` runs three self-contained scenarios that exercise the full system:

### Scenario 1: Hardware Module Attachment (Decorator + Bridge)

**Patterns exercised:** Abstract Factory, Bridge, Decorator, Facade, Singleton

1. Create a `PharmacyKiosk` via `PharmacyKioskFactory` (produces `RoboticArmDispenserImpl`)
2. Run baseline diagnostics (BaseKiosk + RoboticArm)
3. Attach `RefrigerationModule` → diagnostics now include temperature check
4. Attach `SolarMonitorModule` → diagnostics now include solar output
5. Hot-swap dispenser to `SpiralDispenserImpl` via Bridge
6. Run diagnostics again — dispenser changed, decorator modules persist

### Scenario 2: Payment Provider Integration (Adapter + Command)

**Patterns exercised:** Abstract Factory, Adapter, Command, Composite, Proxy, Facade, Singleton

1. Create a `FoodKiosk` via `FoodKioskFactory` (produces `ConveyorDispenserImpl` + `UPIAdapter`)
2. Add a `Sandwich` product to inventory
3. Purchase `Sandwich` via UPI → full Command pipeline (reserve → pay → dispense → finalize)
4. Print transaction history
5. Swap payment provider to `CreditCardAdapter`
6. Purchase `Sandwich` again via CreditCard
7. Issue a refund via `RefundCommand`
8. Print updated transaction history

### Scenario 3: Nested Bundle Inventory (Composite + Proxy)

**Patterns exercised:** Abstract Factory, Composite, Proxy, Command, Facade, Singleton

1. Create an `EmergencyReliefKiosk` via `EmergencyReliefKioskFactory`
2. Add individual products: `Bandage`, `Antiseptic`, `Painkiller`
3. Create `FirstAidKit` bundle (Bandage + Antiseptic)
4. Create `EmergencyKit` bundle (FirstAidKit + Painkiller) — nested two levels deep
5. Display full inventory tree
6. Purchase `EmergencyKit` → recursively deducts stock from all leaf items
7. Display inventory tree (reduced stock)
8. Simulate hardware fault on `Bandage` → `set_hardware_available(False)`
9. Attempt to purchase `EmergencyKit` → **fails** (Bandage unavailable propagates up through bundle)
10. Demonstrate unauthorized `user`-role proxy blocked from `update_stock()`
11. Restore hardware → purchase succeeds again

---

## Desktop GUI (PySide6)

The GUI wraps existing domain logic through `KioskInterface` via `gui/kiosk_controller.py`.
No design-pattern implementation is rewritten; the tabs orchestrate the same flows as
the console scenarios. A role selector lets you switch between `admin`, `technician`,
and `user` views so you can demonstrate different faculty testing paths:

| Tab | What it does | Patterns highlighted |
|---|---|---|
| Kiosk / Hardware | Create kiosk variants, run diagnostics, attach modules, hot-swap dispenser hardware, switch operator role | Abstract Factory, Bridge, Decorator, Facade |
| Inventory | Visualize product/bundle tree, load/save `data/inventory.json`, add products and bundles | Composite, Proxy, Facade |
| Transactions / Payments | Purchase and refund forms, runtime payment adapter swap (UPI/Credit Card/Digital Wallet), kiosk switching | Adapter, Command, Facade |
| History / Logs | Structured command history and singleton event log stream | Command, Singleton |

Run with:

```bash
python run_gui.py
```

---

## Persistence

The system provides JSON-based persistence through three mechanisms:

### Configuration — `CentralRegistry`

```python
registry = CentralRegistry.get_instance()
registry.load_config("data/config.json")   # Load config into status map
registry.save_config("data/config.json")   # Save status map to file
```

**Sample `data/config.json`:**

```json
{
  "kioskId": "KIOSK-001",
  "kioskType": "PharmacyKiosk",
  "activeRole": "admin",
  "emergencyMode": false,
  "maxPurchasePerUser": 5,
  "activePaymentProvider": "CreditCard",
  "kioskRegistry": [
    { "kioskId": "KIOSK-001", "kioskType": "PharmacyKiosk", "role": "admin" },
    { "kioskId": "KIOSK-002", "kioskType": "FoodKiosk", "role": "user" },
    { "kioskId": "KIOSK-003", "kioskType": "EmergencyReliefKiosk", "role": "technician" }
  ]
}
```

### Inventory — `InventoryManager`

```python
manager = InventoryManager()
manager.load_from_file("data/inventory.json")   # Load products and bundles
manager.save_to_file("data/inventory.json")     # Save current state
```

Supports both individual products and bundles (with `isBundle` flag and `children` list).

### Transaction History — `CommandInvoker`

```python
invoker = CommandInvoker()
invoker.persist_history("data/transactions.json")  # Append history as JSON
```

Each entry records: type (PURCHASE/REFUND/RESTOCK), product ID, user ID, amount, timestamp,
and status.

---

## Testing

The project includes a comprehensive unit test suite with **23 test cases** across four
test modules:

| Module | Tests | Patterns Covered |
|---|---|---|
| `test_hardware.py` | 4 tests | Bridge (dispenser hot-swap), Decorator (module chaining) |
| `test_inventory.py` | 5 tests | Composite (product/bundle), Proxy (role-based authorization) |
| `test_payment.py` | 6 tests | Adapter (all 3 adapters + all 3 legacy stubs) |
| `test_transactions.py` | 8 tests | Command (purchase/refund/restock), undo, rollback on payment/dispense failure |

### Key test scenarios:

- **Purchase with auto-rollback** — `test_purchase_payment_failure` and
  `test_purchase_dispense_failure` verify that stock and payment are rolled back when
  downstream steps fail.
- **Command undo** — `test_command_undo` verifies that undoing a successful purchase
  restores stock and refunds payment.
- **Proxy authorization matrix** — `test_proxy_authorization` verifies that admin, technician,
  and user roles have the correct access permissions.
- **Bundle stock calculation** — `test_bundle_stock_calculation` verifies that bundle
  availability is the minimum of its children's stock.

---

## Known Limitations

1. **In-memory state** — The simulation runs entirely in memory; persistence methods
   (`load_from_file`, `save_to_file`, `persist_history`) exist but are not called
   automatically from `main.py`.
2. **No concurrent access** — The system is single-threaded; no locks or thread-safety
   mechanisms are implemented on the Singleton or shared inventory.
3. **Simulated hardware** — All dispenser implementations return `True` unconditionally;
   no real hardware failure simulation beyond the `hardware_available` flag on `Product`.
4. **Simulated payments** — Legacy payment stubs always succeed; no real error paths.
5. **Bundle purchasing** — When purchasing a bundle, stock is deducted from leaf products
   recursively, but the bundle itself does not track a separate stock quantity.
6. **Transaction ID generation** — Uses truncated UUIDs (`uuid4()[:8]`), which have a
   non-zero (though negligible) collision probability.
7. **Proxy bypass** — `KioskInterface.add_product()` intentionally bypasses the proxy
   (`self._inventory.real.add_item(item)`) for setup convenience.

---

## Future Enhancements

- **Database persistence** — Replace JSON files with SQLite or PostgreSQL for robust
  transactional storage.
- **Web interface** — Add a browser-based frontend (Flask/FastAPI) alongside the existing
  PySide6 desktop app.
- **Observer pattern** — Implement real-time event notifications (low stock alerts,
  hardware fault broadcasts) via an Observer/EventBus.
- **Concurrent access** — Add thread-safe locking to `CentralRegistry`, `InventoryManager`,
  and `CommandInvoker` for multi-threaded or async operation.
- **Logging framework** — Replace `print()` statements with Python's `logging` module for
  configurable log levels and file output.
- **CI/CD pipeline** — Add GitHub Actions or similar for automated test execution on every
  push.
- **Additional kiosk types** — Implement new factory variants (e.g., `ElectronicsKioskFactory`,
  `BookstoreKioskFactory`) to demonstrate extensibility.
- **Redo support** — Extend `CommandInvoker` with redo capability using a secondary stack.

---

---

## License

This project was developed as an academic OOP design patterns project.

---

<div align="center">

**Aura Retail OS** · Path B: Modular Hardware Platform · Python 3.10+

</div>
