from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication

from factories.emergency_relief_factory import EmergencyReliefKioskFactory
from factories.food_kiosk_factory import FoodKioskFactory
from factories.pharmacy_kiosk_factory import PharmacyKioskFactory
from gui.main_window import MainWindow


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aura Retail OS PySide6 GUI")
    parser.add_argument(
        "--kiosk-type",
        choices=["pharmacy", "food", "emergency"],
        default="pharmacy",
        help="Initial kiosk factory",
    )
    parser.add_argument(
        "--kiosk-id",
        default="",
        help="Initial kiosk ID (defaults by kiosk type)",
    )
    return parser


def _resolve_initial_kiosk(kiosk_type: str, kiosk_id: str):
    if kiosk_type == "food":
        factory = FoodKioskFactory()
        default_id = "KIOSK-002"
    elif kiosk_type == "emergency":
        factory = EmergencyReliefKioskFactory()
        default_id = "KIOSK-003"
    else:
        factory = PharmacyKioskFactory()
        default_id = "KIOSK-001"

    return factory, kiosk_id or default_id


def _get_stylesheet() -> str:
    return """
QWidget {
    background-color: #12161E;
    color: #E6EDF3;
}
QGroupBox {
    border: 1px solid #2D3748;
    border-radius: 8px;
    margin-top: 12px;
    padding: 8px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget, QTreeWidget, QTableWidget, QTextEdit {
    background-color: #1A202C;
    border: 1px solid #2D3748;
    border-radius: 6px;
    padding: 4px;
}
QPushButton {
    background-color: #0F766E;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #0D9488;
}
QPushButton:pressed {
    background-color: #115E59;
}
QHeaderView::section {
    background-color: #1F2937;
    color: #E6EDF3;
    border: none;
    padding: 6px;
}
"""


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    factory, kiosk_id = _resolve_initial_kiosk(args.kiosk_type, args.kiosk_id)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(_get_stylesheet())

    window = MainWindow(factory, kiosk_id)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

