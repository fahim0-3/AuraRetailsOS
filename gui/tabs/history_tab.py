from __future__ import annotations

from PySide6.QtWidgets import (
    QHeaderView,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.kiosk_controller import KioskController


class HistoryTab(QWidget):
    def __init__(self, controller: KioskController) -> None:
        super().__init__()
        self._controller = controller
        self._build_ui()
        self._wire_signals()
        self.refresh_history_table()
        self._load_event_log()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        self.refresh_btn = QPushButton("Refresh history")
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            ["Index", "Type", "Product ID", "User ID", "Amount", "Status", "Timestamp"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        root.addWidget(self.refresh_btn)
        root.addWidget(self.history_table)
        root.addWidget(self.log_text)

    def _wire_signals(self) -> None:
        self.refresh_btn.clicked.connect(self.refresh_history_table)
        self._controller.history_changed.connect(self.refresh_history_table)
        self._controller.kiosk_changed.connect(self.refresh_history_table)
        self._controller.log_message.connect(self.append_log_line)

    def refresh_history_table(self) -> None:
        rows = self._controller.get_transaction_history()
        self.history_table.setRowCount(len(rows))
        for index, entry in enumerate(rows, start=1):
            self.history_table.setItem(index - 1, 0, QTableWidgetItem(str(index)))
            self.history_table.setItem(index - 1, 1, QTableWidgetItem(entry["type"]))
            self.history_table.setItem(index - 1, 2, QTableWidgetItem(entry["product_id"]))
            self.history_table.setItem(index - 1, 3, QTableWidgetItem(entry["user_id"]))
            self.history_table.setItem(index - 1, 4, QTableWidgetItem(f"{entry['amount']:.2f}"))
            self.history_table.setItem(index - 1, 5, QTableWidgetItem(entry["status"]))
            self.history_table.setItem(index - 1, 6, QTableWidgetItem(entry["timestamp"]))

    def _load_event_log(self) -> None:
        self.log_text.clear()
        logs = self._controller.get_event_log()
        if logs:
            self.log_text.setPlainText("\n".join(logs))

    def append_log_line(self, entry: str) -> None:
        if self.log_text.toPlainText():
            self.log_text.append(entry)
        else:
            self.log_text.setPlainText(entry)

