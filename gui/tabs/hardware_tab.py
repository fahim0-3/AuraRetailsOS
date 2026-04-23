from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

from factories.emergency_relief_factory import EmergencyReliefKioskFactory
from factories.food_kiosk_factory import FoodKioskFactory
from factories.pharmacy_kiosk_factory import PharmacyKioskFactory
from gui.kiosk_controller import KioskController
from hardware.base_kiosk import BaseKiosk
from hardware.conveyor_dispenser import ConveyorDispenserImpl
from hardware.network_module import NetworkModule
from hardware.refrigeration_module import RefrigerationModule
from hardware.robotic_arm_dispenser import RoboticArmDispenserImpl
from hardware.solar_monitor_module import SolarMonitorModule
from hardware.spiral_dispenser import SpiralDispenserImpl


class HardwareTab(QWidget):
    def __init__(self, controller: KioskController) -> None:
        super().__init__()
        self._controller = controller
        self._build_ui()
        self._wire_signals()
        self._refresh_snapshot()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        kiosk_box = QGroupBox("Kiosk Setup")
        kiosk_form = QFormLayout(kiosk_box)
        self.kiosk_type_combo = QComboBox()
        self.kiosk_type_combo.addItems(["Pharmacy", "Food", "Emergency Relief"])
        self.kiosk_id_input = QLineEdit("KIOSK-001")
        self.create_kiosk_btn = QPushButton("Create kiosk")
        kiosk_form.addRow("Kiosk Type", self.kiosk_type_combo)
        kiosk_form.addRow("Kiosk ID", self.kiosk_id_input)
        kiosk_form.addRow("", self.create_kiosk_btn)

        diagnostics_box = QGroupBox("Diagnostics")
        diagnostics_layout = QVBoxLayout(diagnostics_box)
        self.kiosk_info_label = QLabel("-")
        self.dispenser_info_label = QLabel("-")
        self.run_diagnostics_btn = QPushButton("Run diagnostics")
        self.diagnostics_output = QTextEdit()
        self.diagnostics_output.setReadOnly(True)
        diagnostics_layout.addWidget(self.kiosk_info_label)
        diagnostics_layout.addWidget(self.dispenser_info_label)
        diagnostics_layout.addWidget(self.run_diagnostics_btn)
        diagnostics_layout.addWidget(self.diagnostics_output)

        modules_box = QGroupBox("Hardware Modules")
        modules_layout = QHBoxLayout(modules_box)
        self.attach_refrigeration_btn = QPushButton("Attach Refrigeration")
        self.attach_solar_btn = QPushButton("Attach Solar Monitor")
        self.attach_network_btn = QPushButton("Attach Network")
        modules_layout.addWidget(self.attach_refrigeration_btn)
        modules_layout.addWidget(self.attach_solar_btn)
        modules_layout.addWidget(self.attach_network_btn)

        dispenser_box = QGroupBox("Dispenser Hot-Swap")
        dispenser_layout = QHBoxLayout(dispenser_box)
        self.use_spiral_btn = QPushButton("Use Spiral Dispenser")
        self.use_conveyor_btn = QPushButton("Use Conveyor Dispenser")
        self.use_robotic_btn = QPushButton("Use Robotic Arm Dispenser")
        dispenser_layout.addWidget(self.use_spiral_btn)
        dispenser_layout.addWidget(self.use_conveyor_btn)
        dispenser_layout.addWidget(self.use_robotic_btn)

        root.addWidget(kiosk_box)
        root.addWidget(diagnostics_box)
        root.addWidget(modules_box)
        root.addWidget(dispenser_box)

    def _wire_signals(self) -> None:
        self.create_kiosk_btn.clicked.connect(self._create_kiosk)
        self.run_diagnostics_btn.clicked.connect(self._run_diagnostics)

        self.attach_refrigeration_btn.clicked.connect(
            lambda: self._controller.attach_module(RefrigerationModule(BaseKiosk()))
        )
        self.attach_solar_btn.clicked.connect(
            lambda: self._controller.attach_module(SolarMonitorModule(BaseKiosk()))
        )
        self.attach_network_btn.clicked.connect(
            lambda: self._controller.attach_module(NetworkModule(BaseKiosk()))
        )

        self.use_spiral_btn.clicked.connect(
            lambda: self._controller.swap_dispenser(SpiralDispenserImpl())
        )
        self.use_conveyor_btn.clicked.connect(
            lambda: self._controller.swap_dispenser(ConveyorDispenserImpl())
        )
        self.use_robotic_btn.clicked.connect(
            lambda: self._controller.swap_dispenser(RoboticArmDispenserImpl())
        )

        self._controller.kiosk_changed.connect(self._refresh_snapshot)

    def _create_kiosk(self) -> None:
        selected = self.kiosk_type_combo.currentText()
        kiosk_id = self.kiosk_id_input.text().strip()

        if selected == "Pharmacy":
            factory = PharmacyKioskFactory()
            default_id = "KIOSK-001"
        elif selected == "Food":
            factory = FoodKioskFactory()
            default_id = "KIOSK-002"
        else:
            factory = EmergencyReliefKioskFactory()
            default_id = "KIOSK-003"

        if not kiosk_id:
            kiosk_id = default_id
            self.kiosk_id_input.setText(kiosk_id)

        self._controller.create_kiosk(factory, kiosk_id)
        QMessageBox.information(self, "Kiosk Created", f"{selected} kiosk created: {kiosk_id}")

    def _run_diagnostics(self) -> None:
        report = self._controller.get_diagnostics_report()
        self.diagnostics_output.setPlainText(report)

    def _refresh_snapshot(self) -> None:
        snapshot = self._controller.get_kiosk_snapshot()
        self.kiosk_info_label.setText(
            f"Kiosk: {snapshot['kiosk_id']} ({snapshot['kiosk_type']})"
        )
        self.dispenser_info_label.setText(
            f"Dispenser: {snapshot['dispenser_type']}"
        )

