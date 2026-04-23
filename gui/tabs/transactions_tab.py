from __future__ import annotations

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


class TransactionsTab(QWidget):
    def __init__(self, controller: KioskController) -> None:
        super().__init__()
        self._controller = controller
        self._build_ui()
        self._wire_signals()
        self._refresh_product_ids()
        self._sync_provider_from_controller()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

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

        root.addLayout(row)
        root.addWidget(self.result_label)

    def _wire_signals(self) -> None:
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.purchase_btn.clicked.connect(self._on_purchase)
        self.refund_btn.clicked.connect(self._on_refund)
        self._controller.purchase_result.connect(self._on_purchase_result)
        self._controller.refund_result.connect(self._on_refund_result)
        self._controller.inventory_changed.connect(self._refresh_product_ids)
        self._controller.kiosk_changed.connect(self._refresh_product_ids)
        self._controller.kiosk_changed.connect(self._sync_provider_from_controller)

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
        ids = self._flatten_item_ids(snapshot)
        typed_text = self.product_id_combo.currentText()
        self.product_id_combo.blockSignals(True)
        self.product_id_combo.clear()
        self.product_id_combo.addItems(ids)
        if typed_text:
            self.product_id_combo.setEditText(typed_text)
        self.product_id_combo.blockSignals(False)

    def _flatten_item_ids(self, nodes: list[dict[str, Any]]) -> list[str]:
        ids: list[str] = []
        seen: set[str] = set()

        def visit(node: dict[str, Any]) -> None:
            item_id = str(node["id"])
            if item_id not in seen:
                ids.append(item_id)
                seen.add(item_id)
            for child in node.get("children", []):
                visit(child)

        for node in nodes:
            visit(node)
        return ids

    def _sync_provider_from_controller(self) -> None:
        provider = self._controller.get_payment_provider_display_name()
        self.provider_combo.blockSignals(True)
        index = self.provider_combo.findText(provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        self.provider_combo.blockSignals(False)

