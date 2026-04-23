from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.kiosk_controller import KioskController
from inventory.product import Product


class InventoryTab(QWidget):
    def __init__(self, controller: KioskController) -> None:
        super().__init__()
        self._controller = controller
        self._default_inventory_path = str(
            Path(__file__).resolve().parents[2] / "data" / "inventory.json"
        )
        self._build_ui()
        self._wire_signals()
        self.refresh_inventory_tree()
        self.refresh_bundle_children_list()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        controls_row = QHBoxLayout()
        self.load_btn = QPushButton("Load inventory from JSON")
        self.save_btn = QPushButton("Save inventory to JSON")
        self.refresh_btn = QPushButton("Refresh tree")
        controls_row.addWidget(self.load_btn)
        controls_row.addWidget(self.save_btn)
        controls_row.addWidget(self.refresh_btn)

        self.inventory_tree = QTreeWidget()
        self.inventory_tree.setColumnCount(10)
        self.inventory_tree.setHeaderLabels(
            [
                "ID",
                "Name",
                "Price",
                "Total Stock",
                "Reserved",
                "Available",
                "Hardware Available",
                "Is Bundle",
                "Required Modules",
                "Essential",
            ]
        )

        product_box = QGroupBox("Add Product")
        product_form = QFormLayout(product_box)
        self.product_id_input = QLineEdit()
        self.product_name_input = QLineEdit()
        self.product_price_input = QDoubleSpinBox()
        self.product_price_input.setMaximum(1_000_000)
        self.product_price_input.setDecimals(2)
        self.product_stock_input = QSpinBox()
        self.product_stock_input.setMaximum(1_000_000)
        self.product_hw_checkbox = QCheckBox("Hardware available")
        self.product_hw_checkbox.setChecked(True)
        self.product_required_modules_input = QLineEdit()
        self.product_required_modules_input.setPlaceholderText(
            "Comma-separated module keys (e.g. refrigeration,network)"
        )
        self.product_essential_checkbox = QCheckBox("Essential item")
        self.add_product_btn = QPushButton("Add product")
        product_form.addRow("ID", self.product_id_input)
        product_form.addRow("Name", self.product_name_input)
        product_form.addRow("Price", self.product_price_input)
        product_form.addRow("Total Stock", self.product_stock_input)
        product_form.addRow("", self.product_hw_checkbox)
        product_form.addRow("Required Modules", self.product_required_modules_input)
        product_form.addRow("", self.product_essential_checkbox)
        product_form.addRow("", self.add_product_btn)

        bundle_box = QGroupBox("Add Bundle")
        bundle_form = QFormLayout(bundle_box)
        self.bundle_id_input = QLineEdit()
        self.bundle_name_input = QLineEdit()
        self.bundle_children_list = QListWidget()
        self.bundle_children_list.setSelectionMode(QListWidget.MultiSelection)
        self.refresh_children_btn = QPushButton("Refresh children list")
        self.add_bundle_btn = QPushButton("Add bundle")
        bundle_form.addRow("ID", self.bundle_id_input)
        bundle_form.addRow("Name", self.bundle_name_input)
        bundle_form.addRow(QLabel("Children (multi-select)"))
        bundle_form.addRow(self.bundle_children_list)
        bundle_form.addRow("", self.refresh_children_btn)
        bundle_form.addRow("", self.add_bundle_btn)

        forms_row = QHBoxLayout()
        forms_row.addWidget(product_box)
        forms_row.addWidget(bundle_box)

        root.addLayout(controls_row)
        root.addWidget(self.inventory_tree)
        root.addLayout(forms_row)

    def _wire_signals(self) -> None:
        self.load_btn.clicked.connect(self._load_inventory_from_json)
        self.save_btn.clicked.connect(self._save_inventory_to_json)
        self.refresh_btn.clicked.connect(self.refresh_inventory_tree)
        self.refresh_children_btn.clicked.connect(self.refresh_bundle_children_list)
        self.add_product_btn.clicked.connect(self._add_product)
        self.add_bundle_btn.clicked.connect(self._add_bundle)
        self._controller.inventory_changed.connect(self.refresh_inventory_tree)
        self._controller.inventory_changed.connect(self.refresh_bundle_children_list)
        self._controller.kiosk_changed.connect(self.refresh_inventory_tree)
        self._controller.kiosk_changed.connect(self.refresh_bundle_children_list)

    def refresh_inventory_tree(self) -> None:
        self.inventory_tree.clear()
        for item in self._controller.get_inventory_snapshot():
            self._append_tree_item(None, item)
        self.inventory_tree.expandAll()

    def refresh_bundle_children_list(self) -> None:
        self.bundle_children_list.clear()
        for item_id in self._flatten_item_ids(self._controller.get_inventory_snapshot()):
            list_item = QListWidgetItem(item_id)
            list_item.setData(Qt.UserRole, item_id)
            self.bundle_children_list.addItem(list_item)

    def _append_tree_item(self, parent: QTreeWidgetItem | None, item: dict[str, Any]) -> None:
        row = QTreeWidgetItem(
            [
                str(item["id"]),
                str(item["name"]),
                f"{float(item['price']):.2f}",
                str(item["total_stock"]),
                str(item["reserved_stock"]),
                str(item["available_stock"]),
                "Yes" if item["hardware_available"] else "No",
                "Yes" if item["is_bundle"] else "No",
                ", ".join(item.get("required_modules", [])),
                "Yes" if item.get("essential_item", False) else "No",
            ]
        )
        if parent is None:
            self.inventory_tree.addTopLevelItem(row)
        else:
            parent.addChild(row)
        for child in item.get("children", []):
            self._append_tree_item(row, child)

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

    def _load_inventory_from_json(self) -> None:
        self._controller.load_inventory_from_json(self._default_inventory_path)

    def _save_inventory_to_json(self) -> None:
        self._controller.save_inventory_to_json(self._default_inventory_path)

    def _add_product(self) -> None:
        item_id = self.product_id_input.text().strip()
        name = self.product_name_input.text().strip()
        price = float(self.product_price_input.value())
        stock = int(self.product_stock_input.value())
        hardware_available = self.product_hw_checkbox.isChecked()
        required_modules = [
            token.strip().lower()
            for token in self.product_required_modules_input.text().split(",")
            if token.strip()
        ]
        essential_item = self.product_essential_checkbox.isChecked()

        if not item_id or not name:
            QMessageBox.warning(self, "Invalid Input", "Product ID and name are required.")
            return

        product = Product(
            item_id=item_id,
            name=name,
            price=price,
            total_stock=stock,
            hardware_available=hardware_available,
            required_modules=required_modules,
            essential_item=essential_item,
        )
        if self._controller.add_product(product):
            self.product_id_input.clear()
            self.product_name_input.clear()
            self.product_price_input.setValue(0.0)
            self.product_stock_input.setValue(0)
            self.product_hw_checkbox.setChecked(True)
            self.product_required_modules_input.clear()
            self.product_essential_checkbox.setChecked(False)
        else:
            QMessageBox.warning(self, "Add Product Failed", f"Product ID already exists: {item_id}")

    def _add_bundle(self) -> None:
        bundle_id = self.bundle_id_input.text().strip()
        bundle_name = self.bundle_name_input.text().strip()
        child_ids = [
            str(item.data(Qt.UserRole))
            for item in self.bundle_children_list.selectedItems()
        ]

        if not bundle_id or not bundle_name:
            QMessageBox.warning(self, "Invalid Input", "Bundle ID and name are required.")
            return
        if not child_ids:
            QMessageBox.warning(self, "Invalid Input", "Select at least one child item.")
            return

        if self._controller.add_bundle(bundle_id, bundle_name, child_ids):
            self.bundle_id_input.clear()
            self.bundle_name_input.clear()
            for i in range(self.bundle_children_list.count()):
                self.bundle_children_list.item(i).setSelected(False)
        else:
            QMessageBox.warning(self, "Add Bundle Failed", f"Could not add bundle {bundle_id}.")

