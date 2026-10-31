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
