from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.kiosk_controller import KioskController
from inventory.kiosk_compatibility import kiosk_matches, normalize_kiosk_tag


class TransactionsTab(QWidget):
    def __init__(self, controller: KioskController) -> None:
        super().__init__()
        self._controller = controller
        self._default_inventory_path = str(
            Path(__file__).resolve().parents[2] / "data" / "inventory.json"
        )
        self._build_ui()
        self._wire_signals()
        self._refresh_product_ids()
        self._sync_provider_from_controller()
        self._sync_kiosk_controls()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        kiosk_box = QGroupBox("Kiosk Context")
        kiosk_form = QFormLayout(kiosk_box)
        self.current_kiosk_label = QLabel("-")
        self.current_role_label = QLabel("-")
        self.switch_kiosk_combo = QComboBox()
        self.switch_kiosk_combo.addItems(list(self._controller.KIOSK_TYPE_OPTIONS))
        self.switch_kiosk_id_input = QLineEdit()
        self.switch_kiosk_btn = QPushButton("Switch kiosk")
        kiosk_form.addRow("Current", self.current_kiosk_label)
        kiosk_form.addRow("Role", self.current_role_label)
        kiosk_form.addRow("Switch to", self.switch_kiosk_combo)
        kiosk_form.addRow("Kiosk ID", self.switch_kiosk_id_input)
        kiosk_form.addRow("", self.switch_kiosk_btn)

        purchase_box = QGroupBox("Purchase")
        purchase_form = QFormLayout(purchase_box)
        self.product_id_combo = QComboBox()
        self.product_id_combo.setEditable(True)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1_000)
        self.user_id_input = QLineEdit("USER-001")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["UPI", "Credit Card", "Digital Wallet"])
        self.purchase_btn = QPushButton("Purchase")
        purchase_form.addRow("Product ID", self.product_id_combo)
        purchase_form.addRow("Quantity", self.quantity_spin)
        purchase_form.addRow("User ID", self.user_id_input)
        purchase_form.addRow("Payment Provider", self.provider_combo)
        purchase_form.addRow("", self.purchase_btn)

        refund_box = QGroupBox("Refund")
        refund_form = QFormLayout(refund_box)
        self.transaction_id_input = QLineEdit()
        self.refund_amount_spin = QDoubleSpinBox()
        self.refund_amount_spin.setRange(0.01, 1_000_000)
        self.refund_amount_spin.setDecimals(2)
        self.refund_btn = QPushButton("Refund")
        refund_form.addRow("Transaction ID", self.transaction_id_input)
        refund_form.addRow("Amount", self.refund_amount_spin)
        refund_form.addRow("", self.refund_btn)

        self.result_label = QLabel("Ready")

        row = QHBoxLayout()
        row.addWidget(purchase_box)
        row.addWidget(refund_box)

        root.addWidget(kiosk_box)
        root.addLayout(row)
        root.addWidget(self.result_label)

    def _wire_signals(self) -> None:
        self.switch_kiosk_btn.clicked.connect(self._on_switch_kiosk)
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.purchase_btn.clicked.connect(self._on_purchase)
        self.refund_btn.clicked.connect(self._on_refund)
        self._controller.purchase_result.connect(self._on_purchase_result)
        self._controller.refund_result.connect(self._on_refund_result)
        self._controller.inventory_changed.connect(self._refresh_product_ids)
        self._controller.kiosk_changed.connect(self._refresh_product_ids)
        self._controller.kiosk_changed.connect(self._sync_kiosk_controls)
        self._controller.kiosk_changed.connect(self._refresh_permissions)
        self._controller.kiosk_changed.connect(self._sync_provider_from_controller)
        self._refresh_permissions()

    def _on_provider_changed(self, provider_name: str) -> None:
        self._controller.set_payment_provider(provider_name)

    def _on_purchase(self) -> None:
        product_id = self.product_id_combo.currentText().strip()
        user_id = self.user_id_input.text().strip()
        quantity = self.quantity_spin.value()
        self._controller.purchase(product_id, user_id, quantity)

    def _on_refund(self) -> None:
        transaction_id = self.transaction_id_input.text().strip()
        amount = self.refund_amount_spin.value()
        self._controller.refund(transaction_id, amount)

    def _on_switch_kiosk(self) -> None:
        target = self.switch_kiosk_combo.currentText()
        kiosk_id = self.switch_kiosk_id_input.text().strip()
        success = self._controller.switch_kiosk_type(
            target,
            kiosk_id=kiosk_id,
            inventory_path=self._default_inventory_path,
        )
        if not success:
            QMessageBox.warning(self, "Switch kiosk", "Unsupported kiosk type selected.")
            return
        self.result_label.setText(f"Kiosk switched to {target}.")

    def _on_purchase_result(self, success: bool, message: str) -> None:
        self.result_label.setText(message)
        if success:
            QMessageBox.information(self, "Purchase", message)
        else:
            QMessageBox.warning(self, "Purchase", message)

    def _on_refund_result(self, success: bool, message: str) -> None:
        self.result_label.setText(message)
        if success:
            QMessageBox.information(self, "Refund", message)
        else:
            QMessageBox.warning(self, "Refund", message)

    def _refresh_product_ids(self) -> None:
        snapshot = self._controller.get_inventory_snapshot()
        kiosk_type = self._controller.get_kiosk_snapshot().get("kiosk_type", "")
        ids = self._flatten_item_ids(snapshot, str(kiosk_type))
        typed_text = self.product_id_combo.currentText()
        self.product_id_combo.blockSignals(True)
        self.product_id_combo.clear()
        self.product_id_combo.addItems(ids)
        if typed_text:
            self.product_id_combo.setEditText(typed_text)
        self.product_id_combo.blockSignals(False)

    def _flatten_item_ids(self, nodes: list[dict[str, Any]], kiosk_type: str) -> list[str]:
        ids: list[str] = []
        seen: set[str] = set()

        def visit(node: dict[str, Any]) -> None:
            item_id = str(node["id"])
            if item_id not in seen and self._is_compatible_for_kiosk(node, kiosk_type):
                ids.append(item_id)
                seen.add(item_id)
            for child in node.get("children", []):
                visit(child)

        for node in nodes:
            visit(node)
        return ids

    def _is_compatible_for_kiosk(self, node: dict[str, Any], kiosk_type: str) -> bool:
        values = node.get("compatible_kiosks", node.get("compatibleKiosks", []))
        if not isinstance(values, list):
            values = []
        return kiosk_matches(values, kiosk_type)

    def _sync_provider_from_controller(self) -> None:
        provider = self._controller.get_payment_provider_display_name()
        self.provider_combo.blockSignals(True)
        index = self.provider_combo.findText(provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        self.provider_combo.blockSignals(False)

    def _sync_kiosk_controls(self) -> None:
        snapshot = self._controller.get_kiosk_snapshot()
        kiosk_id = str(snapshot.get("kiosk_id", ""))
        kiosk_type = str(snapshot.get("kiosk_type", ""))
        role = str(snapshot.get("operator_role", self._controller.get_operator_role()))
        normalized = normalize_kiosk_tag(kiosk_type)
        label_map = {
            "pharmacy": "Pharmacy",
            "food": "Food",
            "emergency": "Emergency Relief",
        }
        selected_label = label_map.get(normalized, "Pharmacy")
        self.current_kiosk_label.setText(f"{selected_label} ({kiosk_id})")
        self.current_role_label.setText(role)

        self.switch_kiosk_combo.blockSignals(True)
        idx = self.switch_kiosk_combo.findText(selected_label)
        if idx >= 0:
            self.switch_kiosk_combo.setCurrentIndex(idx)
        self.switch_kiosk_combo.blockSignals(False)
        self.switch_kiosk_id_input.setText(kiosk_id)

    def _refresh_permissions(self) -> None:
        role = self._controller.get_operator_role()
        can_administer = role in {"admin", "technician"}
        self.provider_combo.setEnabled(can_administer)
        self.switch_kiosk_btn.setEnabled(can_administer)
        self.switch_kiosk_combo.setEnabled(can_administer)
        self.switch_kiosk_id_input.setEnabled(can_administer)
        self.refund_btn.setEnabled(can_administer)
