# ============================================================
# Subsystem: CentralRegistry  Pattern: Singleton  Role: System-wide logging and status
# ============================================================

from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Optional


# PATTERN: Singleton
class CentralRegistry:
    _instance = None

    def __new__(cls) -> CentralRegistry:
        if CentralRegistry._instance is None:
            CentralRegistry._instance = super().__new__(cls)
            CentralRegistry._instance._status_map = {}
            CentralRegistry._instance._event_log = []
        return CentralRegistry._instance

    @staticmethod
    def get_instance() -> CentralRegistry:
        return CentralRegistry()

    def log_event(self, event: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
        entry = f"[{timestamp}] {event}"
        self._event_log.append(entry)

    def get_status(self, key: str) -> Optional[str]:
        return self._status_map.get(key)

    def set_status(self, key: str, value: str) -> None:
        self._status_map[key] = value

    def get_event_log(self) -> list[str]:
        return self._event_log.copy()

    def load_config(self, filepath: str) -> dict:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            for key, value in data.items():
                self.set_status(key, str(value))
            return data
        except FileNotFoundError:
            return {}

    def save_config(self, filepath: str) -> None:
        with open(filepath, 'w') as f:
            json.dump(self._status_map, f, indent=2)
