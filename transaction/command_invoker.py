# ============================================================
# Subsystem: Transaction  Pattern: Command  Role: Command invoker
# ============================================================

from __future__ import annotations
import json
from typing import TYPE_CHECKING

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

    def persist_history(self, filepath: str) -> None:
        entries = []
        for cmd in self._history:
            if hasattr(cmd, '_product_id'):
                entry_type = "PURCHASE"
                product_id = cmd._product_id  # type: ignore
                user_id = cmd._user_id  # type: ignore
            elif hasattr(cmd, '_transaction_id'):
                entry_type = "REFUND"
                product_id = ""
                user_id = ""
            else:
                entry_type = "RESTOCK"
                product_id = cmd._product_id  # type: ignore
                user_id = ""
            entry = {
                "id": getattr(cmd, '_transaction_id', '') or getattr(cmd, '_product_id', ''),
                "type": entry_type,
                "productId": product_id,
                "userId": user_id,
                "amount": getattr(cmd, '_amount', 0.0),
                "timestamp": cmd.timestamp,
                "status": cmd.status,
            }
            entries.append(entry)
        with open(filepath, 'a') as f:
            json.dump(entries, f, indent=2)
            f.write("\n")
