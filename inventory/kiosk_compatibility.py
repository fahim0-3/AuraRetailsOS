from __future__ import annotations

from collections.abc import Iterable


def normalize_kiosk_tag(value: str) -> str:
    compact = "".join(ch for ch in value.strip().lower() if ch.isalnum())
    if compact.endswith("kiosk"):
        compact = compact[:-5]

    aliases = {
        "pharmacy": "pharmacy",
        "food": "food",
        "emergency": "emergency",
        "emergencyrelief": "emergency",
    }
    return aliases.get(compact, compact)


def normalize_kiosk_tags(values: Iterable[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        tag = normalize_kiosk_tag(str(value))
        if tag:
            normalized.add(tag)
    return normalized


def normalize_module_tag(value: str) -> str:
    compact = "".join(ch for ch in value.strip().lower() if ch.isalnum())
    aliases = {
        "solar": "solar_monitor",
        "solarmonitor": "solar_monitor",
        "solar_monitor": "solar_monitor",
        "refrigeration": "refrigeration",
        "fridge": "refrigeration",
        "coldchain": "refrigeration",
        "network": "network",
        "base": "base",
    }
    return aliases.get(compact, compact)


def normalize_module_tags(values: Iterable[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        tag = normalize_module_tag(str(value))
        if tag:
            normalized.add(tag)
    return normalized


def kiosk_matches(allowed_kiosks: Iterable[str], kiosk_type: str) -> bool:
    normalized_allowed = normalize_kiosk_tags(allowed_kiosks)
    if not normalized_allowed:
        return True

    current = normalize_kiosk_tag(kiosk_type)
    if not current:
        return False
    return current in normalized_allowed


def module_matches(required_modules: Iterable[str], available_modules: Iterable[str]) -> set[str]:
    required = normalize_module_tags(required_modules)
    available = normalize_module_tags(available_modules)
    return required - available

