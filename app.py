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
            return jsonify({"error": "Request body must be valid JSON."}), 400
        try:
            item = update_item(item_id, payload)
        except InventoryError as error:
            code = 404 if "not found" in str(error).lower() else 400
            return jsonify({"error": str(error)}), code
        return jsonify(item), 200

    @app.delete("/inventory/<int:item_id>")
    def remove_inventory_item(item_id):
        """Delete an item and return the deleted object."""
        try:
            deleted = delete_item(item_id)
        except InventoryError as error:
            return jsonify({"error": str(error)}), 404
        return jsonify({"message": "Inventory item deleted.", "item": deleted}), 200

    @app.get("/external-products/search")
    def search_external_products():
        """Search OpenFoodFacts using a barcode or product-name query."""
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "A query parameter is required."}), 400
        try:
            products = search_open_food_facts(query)
        except ExternalAPIError as error:
            return jsonify({"error": str(error)}), 502
        return jsonify({"query": query, "products": products}), 200

    @app.get("/health")
    def health_check():
        """Return a simple service health response."""
        return jsonify({"status": "ok", "service": "inventory-api"}), 200

    @app.errorhandler(404)
    def handle_unknown_route(error):
        """Return JSON instead of Flask's default HTML error."""
        return jsonify({"error": "Route not found."}), 404

    @app.errorhandler(405)
    def handle_wrong_method(error):
        """Return JSON when a route receives the wrong HTTP method."""
        return jsonify({"error": "HTTP method is not allowed for this route."}), 405

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
