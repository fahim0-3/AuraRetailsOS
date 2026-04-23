# ============================================================
# Subsystem: Transaction  Pattern: Command  Role: Command invoker
# ============================================================

from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any

from transaction.i_command import ICommand

if TYPE_CHECKING:
    pass


# PATTERN: Command (Invoker)
class CommandInvoker:
    def __init__(self) -> None:
        self._history: list[ICommand] = []

    def execute_command(self, cmd: ICommand) -> bool:
        success = cmd.execute()
        self._history.append(cmd)
        return success

    def undo_last(self) -> bool:
        if not self._history:
            return False
        cmd = self._history[-1]
        return cmd.undo()

    def print_history(self) -> None:
        for cmd in self._history:
            print(f"  [{cmd.timestamp}] {cmd.get_description()}")

    def _build_history_entry(self, cmd: ICommand) -> dict[str, Any]:
        command_type = cmd.__class__.__name__

        if command_type == "PurchaseItemCommand":
            entry_type = "PURCHASE"
        elif command_type == "RefundCommand":
            entry_type = "REFUND"
        elif command_type == "RestockCommand":
            entry_type = "RESTOCK"
        else:
            entry_type = command_type.upper()

        return {
            "type": entry_type,
            "product_id": getattr(cmd, "_product_id", ""),
            "user_id": getattr(cmd, "_user_id", ""),
            "transaction_id": getattr(cmd, "_transaction_id", ""),
            "amount": float(getattr(cmd, "_amount", 0.0)),
            "status": cmd.status,
            "timestamp": cmd.timestamp,
        }

    def get_history(self) -> list[dict[str, Any]]:
        return [self._build_history_entry(cmd) for cmd in self._history]

    def persist_history(self, filepath: str) -> None:
        entries = [
            {
                "id": entry["transaction_id"] or entry["product_id"],
                "type": entry["type"],
                "productId": entry["product_id"],
                "userId": entry["user_id"],
                "amount": entry["amount"],
                "timestamp": entry["timestamp"],
                "status": entry["status"],
            }
            for entry in self.get_history()
        ]
        with open(filepath, 'a') as f:
            json.dump(entries, f, indent=2)
            f.write("\n")
