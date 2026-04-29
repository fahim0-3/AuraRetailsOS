from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
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

        role_box = QGroupBox("Operator Role")
        role_form = QFormLayout(role_box)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "technician", "user"])
        self.role_apply_btn = QPushButton("Apply role")
        self.current_role_label = QLabel("-")
        role_form.addRow("Current", self.current_role_label)
        role_form.addRow("Select", self.role_combo)
        role_form.addRow("", self.role_apply_btn)

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

        mode_box = QGroupBox("Kiosk Mode")
        mode_layout = QHBoxLayout(mode_box)
        self.emergency_mode_btn = QPushButton("Emergency Mode: OFF")
        self.emergency_mode_btn.setCheckable(True)
        self.maintenance_mode_btn = QPushButton("Maintenance Mode: OFF")
        self.maintenance_mode_btn.setCheckable(True)
        mode_layout.addWidget(self.emergency_mode_btn)
        mode_layout.addWidget(self.maintenance_mode_btn)

        root.addWidget(kiosk_box)
        root.addWidget(role_box)
        root.addWidget(diagnostics_box)
        root.addWidget(modules_box)
        root.addWidget(dispenser_box)
        root.addWidget(mode_box)

    def _wire_signals(self) -> None:
        self.create_kiosk_btn.clicked.connect(self._create_kiosk)
        self.role_apply_btn.clicked.connect(self._apply_role)
        self.run_diagnostics_btn.clicked.connect(self._run_diagnostics)

        self.attach_refrigeration_btn.clicked.connect(
            lambda: self._controller.attach_module(RefrigerationModule(self._controller.kiosk._module_chain))
        )
        self.attach_solar_btn.clicked.connect(
            lambda: self._controller.attach_module(SolarMonitorModule(self._controller.kiosk._module_chain))
        )
        self.attach_network_btn.clicked.connect(
            lambda: self._controller.attach_module(NetworkModule(self._controller.kiosk._module_chain))
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

        self.emergency_mode_btn.clicked.connect(self._toggle_emergency_mode)
        self.maintenance_mode_btn.clicked.connect(self._toggle_maintenance_mode)

        self._controller.kiosk_changed.connect(self._refresh_snapshot)
        self._controller.kiosk_changed.connect(self._refresh_permissions)
        self._controller.kiosk_changed.connect(self._refresh_role_label)
        self._refresh_role_label()
        self._refresh_permissions()

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

    def _apply_role(self) -> None:
        role = self.role_combo.currentText()
        password = None
        if role in {"admin", "technician"}:
            password, accepted = QInputDialog.getText(
                self,
                "Role Password",
                f"Enter the password for {role}:",
                QLineEdit.EchoMode.Password,
            )
            if not accepted:
                return

        if not self._controller.set_operator_role(role, password):
            QMessageBox.warning(
                self,
                "Role Change Failed",
                "Role change rejected. Check the selected role and password.",
            )
            return
        self._refresh_role_label()
        self._refresh_permissions()
        QMessageBox.information(self, "Role Applied", f"Operator role set to {role}.")

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

    def _toggle_emergency_mode(self) -> None:
        is_on = self.emergency_mode_btn.isChecked()
        self._controller.set_emergency_mode(is_on)
        self.emergency_mode_btn.setText(f"Emergency Mode: {'ON' if is_on else 'OFF'}")

    def _toggle_maintenance_mode(self) -> None:
        is_on = self.maintenance_mode_btn.isChecked()
        self._controller.set_kiosk_mode("maintenance" if is_on else "service")
        self.maintenance_mode_btn.setText(f"Maintenance Mode: {'ON' if is_on else 'OFF'}")

    def _refresh_role_label(self) -> None:
        role = self._controller.get_operator_role()
        self.current_role_label.setText(role)
        index = self.role_combo.findText(role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)

    def _refresh_permissions(self) -> None:
        role = self._controller.get_operator_role()
        can_manage_hardware = role in {"admin", "technician"}

        self.create_kiosk_btn.setEnabled(can_manage_hardware)
        self.attach_refrigeration_btn.setEnabled(can_manage_hardware)
        self.attach_solar_btn.setEnabled(can_manage_hardware)
        self.attach_network_btn.setEnabled(can_manage_hardware)
        self.use_spiral_btn.setEnabled(can_manage_hardware)
        self.use_conveyor_btn.setEnabled(can_manage_hardware)
        self.use_robotic_btn.setEnabled(can_manage_hardware)
        self.emergency_mode_btn.setEnabled(can_manage_hardware)
        self.maintenance_mode_btn.setEnabled(can_manage_hardware)
        self.role_apply_btn.setEnabled(True)

