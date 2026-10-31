"""Business logic for the simulated inventory database.

The assignment specifically asks for an array-like data store instead of a
SQL database. Python's list of dictionaries provides that temporary store.
The functions below keep validation separate from Flask route definitions.
"""

from copy import deepcopy
from datetime import datetime, timezone


class InventoryError(Exception):
    """Raised when an inventory operation cannot be completed."""


INITIAL_ITEMS = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "barcode": "000111222333",
        "brand": "Silk",
        "category": "Beverages",
        "price": 450.0,
        "stock": 10,
        "ingredients": "Filtered water, almonds, cane sugar",
        "created_at": "2026-01-01T08:00:00+00:00",
    },
    {
        "id": 2,
        "name": "Whole Grain Cereal",
        "barcode": "000444555666",
        "brand": "Harvest Foods",
        "category": "Breakfast",
        "price": 620.0,
        "stock": 15,
        "ingredients": "Whole grains, raisins, sunflower seeds",
        "created_at": "2026-01-02T08:00:00+00:00",
    },
]

_inventory = deepcopy(INITIAL_ITEMS)
_next_id = 3


def reset_inventory():
    """Restore predictable sample data for tests and demonstrations."""
    global _inventory, _next_id
    _inventory = deepcopy(INITIAL_ITEMS)
    _next_id = 3


def get_all_items():
    """Return a copy so callers cannot mutate storage accidentally."""
    return deepcopy(_inventory)


def get_item(item_id):
    """Find one item or raise a clear not-found error."""
    for item in _inventory:
        if item["id"] == item_id:
            return deepcopy(item)
    raise InventoryError(f"Inventory item with id {item_id} was not found.")


def _require_text(payload, field):
    """Validate a required non-empty text field."""
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise InventoryError(f"'{field}' must be a non-empty string.")
    return value.strip()


def _require_non_negative_number(payload, field):
    """Validate a number that cannot be negative."""
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InventoryError(f"'{field}' must be a number.")
    if value < 0:
        raise InventoryError(f"'{field}' cannot be negative.")
    return float(value)


def _validate_new_item(payload):
    """Build a clean item from a request payload."""
    if not isinstance(payload, dict):
        raise InventoryError("Request data must be a JSON object.")
    item = {
        "name": _require_text(payload, "name"),
        "barcode": str(payload.get("barcode", "")).strip(),
        "brand": str(payload.get("brand", "Unknown")).strip() or "Unknown",
        "category": str(payload.get("category", "General")).strip() or "General",
        "price": _require_non_negative_number(payload, "price"),
        "stock": int(_require_non_negative_number(payload, "stock")),
        "ingredients": str(payload.get("ingredients", "")).strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return item


def add_item(payload):
    """Validate, assign an ID, store, and return a new inventory item."""
    global _next_id
    item = _validate_new_item(payload)
    item["id"] = _next_id
    _next_id += 1
    _inventory.append(item)
    return deepcopy(item)


def update_item(item_id, changes):
    """Patch allowed fields while preserving the item's ID."""
    if not isinstance(changes, dict) or not changes:
        raise InventoryError("Patch data must be a non-empty JSON object.")
    for item in _inventory:
        if item["id"] == item_id:
            if "name" in changes:
                item["name"] = _require_text(changes, "name")
            if "price" in changes:
                item["price"] = _require_non_negative_number(changes, "price")
            if "stock" in changes:
                item["stock"] = int(_require_non_negative_number(changes, "stock"))
            for field in ("barcode", "brand", "category", "ingredients"):
                if field in changes:
                    item[field] = str(changes[field]).strip()
            return deepcopy(item)
    raise InventoryError(f"Inventory item with id {item_id} was not found.")


def delete_item(item_id):
    """Remove an item and return the removed copy."""
    for index, item in enumerate(_inventory):
        if item["id"] == item_id:
            return deepcopy(_inventory.pop(index))
    raise InventoryError(f"Inventory item with id {item_id} was not found.")
