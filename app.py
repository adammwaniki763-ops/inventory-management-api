"""Flask REST API for the inventory-management summative lab.

The application uses an in-memory list as simulated storage, exactly as the
assignment requests. It exposes CRUD routes and an external product search
helper route. Keeping route logic here and data logic in inventory.py makes
the project easier to test and maintain.
"""

from flask import Flask, jsonify, request

from external_api import ExternalAPIError, search_open_food_facts
from inventory import (
    InventoryError,
    add_item,
    delete_item,
    get_all_items,
    get_item,
    update_item,
)


def create_app():
    """Create and configure a Flask application instance."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    @app.get("/inventory")
    def list_inventory():
        """Return all items currently in simulated storage."""
        return jsonify(get_all_items()), 200

    @app.get("/inventory/<int:item_id>")
    def retrieve_inventory_item(item_id):
        """Return one item by its integer identifier."""
        try:
            item = get_item(item_id)
        except InventoryError as error:
            return jsonify({"error": str(error)}), 404
        return jsonify(item), 200

    @app.post("/inventory")
    def create_inventory_item():
        """Validate JSON and create a new inventory item."""
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400
        try:
            item = add_item(payload)
        except InventoryError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify(item), 201

    @app.patch("/inventory/<int:item_id>")
    def edit_inventory_item(item_id):
        """Update only fields supplied for an existing item."""
        payload = request.get_json(silent=True)
        if payload is None:
