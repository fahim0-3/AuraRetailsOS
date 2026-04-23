from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from core.abstract_kiosk_factory import AbstractKioskFactory
from gui.kiosk_controller import KioskController
from gui.tabs.hardware_tab import HardwareTab
from gui.tabs.history_tab import HistoryTab
from gui.tabs.inventory_tab import InventoryTab
from gui.tabs.transactions_tab import TransactionsTab


class MainWindow(QMainWindow):
    def __init__(self, initial_factory: AbstractKioskFactory, kiosk_id: str) -> None:
        super().__init__()
        self.setWindowTitle("Aura Retail OS - PySide6 Console Simulator GUI")
        self.resize(1280, 860)

        self.controller = KioskController(initial_factory, kiosk_id)

        tabs = QTabWidget()
        tabs.addTab(HardwareTab(self.controller), "Kiosk / Hardware")
        tabs.addTab(InventoryTab(self.controller), "Inventory")
        tabs.addTab(TransactionsTab(self.controller), "Transactions / Payments")
        tabs.addTab(HistoryTab(self.controller), "History / Logs")

        self.setCentralWidget(tabs)

