# ============================================================
# Subsystem: Inventory  Pattern: Proxy  Role: Real subject — manages inventory items
# ============================================================

from __future__ import annotations
import json
from typing import Optional, TYPE_CHECKING

from inventory.i_inventory_manager import IInventoryManager

if TYPE_CHECKING:
    from inventory.i_inventory_item import IInventoryItem
    from inventory.product import Product
    from inventory.product_bundle import ProductBundle


class InventoryManager(IInventoryManager):
    def __init__(self) -> None:
        self._items: dict[str, IInventoryItem] = {}

    def get_item(self, item_id: str) -> Optional[IInventoryItem]:
        return self._items.get(item_id)

    def add_item(self, item: IInventoryItem) -> bool:
        if item.item_id in self._items:
            return False
        self._items[item.item_id] = item
        return True

    def update_stock(self, item_id: str, delta: int) -> bool:
        """Handles simple reservation (negative) and rollback/release (positive)"""
        item = self._items.get(item_id)
        if not item:
            return False

        if not item.is_bundle():
            product = item  # type: Product
            if delta < 0:
                avail = product.get_available_stock()
                if avail < abs(delta):
                    return False
                product.reserve(abs(delta))
            else:
                product.release(delta)
        else:
            bundle = item  # type: ProductBundle
            if delta < 0:
                # Check all children first
                if not bundle.is_available() or bundle.get_available_stock() < abs(delta):
                    return False
                for child in bundle._children:
                    self.update_stock(child.item_id, delta)
            else:
                for child in bundle._children:
                    self.update_stock(child.item_id, delta)
        return True

    def restock(self, item_id: str, qty: int) -> bool:
        """Increases total stock of a product"""
        item = self._items.get(item_id)
        if not item or item.is_bundle():
            return False
        
        product = item  # type: Product
        product.restock(qty)
        return True

    def deduct_total_stock(self, item_id: str, qty: int) -> bool:
        """Decreases total stock of a product"""
        item = self._items.get(item_id)
        if not item or item.is_bundle():
            return False
        
        product = item  # type: Product
        product.deduct(qty)
        return True

    def finalize_purchase(self, item_id: str, qty: int) -> bool:
        """Permanently deducts from total stock and clears reservation"""
        item = self._items.get(item_id)
        if not item:
            return False

        if not item.is_bundle():
            product = item  # type: Product
            product.deduct(qty)
            product.release(qty)
        else:
            bundle = item  # type: ProductBundle
            for child in bundle._children:
                self.finalize_purchase(child.item_id, qty)
        return True

    def list_all(self) -> None:
        for item in self._items.values():
            item.display(0)

    def load_from_file(self, filepath: str) -> None:
        with open(filepath, 'r') as f:
            data = json.load(f)

        for entry in data:
            if entry.get("isBundle", False):
                bundle = ProductBundle(entry["id"], entry["name"])
                for child_id in entry.get("children", []):
                    child = self._items.get(child_id)
                    if child:
                        bundle.add_item(child)
                self._items[bundle.item_id] = bundle
            else:
                product = Product(
                    item_id=entry["id"],
                    name=entry["name"],
                    price=entry["price"],
                    total_stock=entry.get("stock", 0),
                    reserved_stock=entry.get("reserved", 0),
                    hardware_available=entry.get("hardwareAvailable", True),
                )
                self._items[product.item_id] = product

    def save_to_file(self, filepath: str) -> None:
        entries = []
        for item in self._items.values():
            if item.is_bundle():
                entries.append({
                    "id": item.item_id,
                    "name": item.name,
                    "isBundle": True,
                    "children": [c.item_id for c in item._children],  # type: ignore
                })
            else:
                product = item  # type: Product
                entries.append({
                    "id": product.item_id,
                    "name": product.name,
                    "price": product.price,
                    "stock": product._total_stock,
                    "reserved": product._reserved_stock,
                    "hardwareAvailable": product._hardware_available,
                    "isBundle": False,
                })
        with open(filepath, 'w') as f:
            json.dump(entries, f, indent=2)
