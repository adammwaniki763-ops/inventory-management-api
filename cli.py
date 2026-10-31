"""Interactive command-line client for the Flask inventory API.

Run the Flask server first, then run this module in another terminal. The CLI
uses HTTP requests instead of importing the storage list, demonstrating how
a real frontend or separate client would communicate with a REST API.
"""

import argparse
import json
import sys

import requests


DEFAULT_BASE_URL = "http://127.0.0.1:5000"


def request_api(method, base_url, path, payload=None, params=None):
    """Send a request and return a friendly result tuple."""
    url = f"{base_url.rstrip('/')}{path}"
    try:
        response = requests.request(method, url, json=payload, params=params, timeout=10)
    except requests.RequestException as error:
        return False, {"error": f"Could not contact API: {error}"}
    try:
        data = response.json()
    except ValueError:
        data = {"error": response.text or "API returned no JSON."}
    return response.ok, data


def print_result(success, data):
    """Print an API result as readable JSON."""
    prefix = "SUCCESS" if success else "ERROR"
    print(f"\n[{prefix}]")
    print(json.dumps(data, indent=2))


def list_items(base_url):
    """Display all inventory items."""
    print_result(*request_api("GET", base_url, "/inventory"))


def view_item(base_url, item_id):
    """Display one item."""
    print_result(*request_api("GET", base_url, f"/inventory/{item_id}"))


def add_item(base_url):
    """Collect fields interactively and create an item."""
    payload = {
        "name": input("Name: ").strip(),
        "barcode": input("Barcode (optional): ").strip(),
        "brand": input("Brand (optional): ").strip(),
        "category": input("Category (optional): ").strip(),
        "price": float(input("Price: ")),
        "stock": int(input("Stock: ")),
        "ingredients": input("Ingredients (optional): ").strip(),
    }
    print_result(*request_api("POST", base_url, "/inventory", payload=payload))


def update_item(base_url, item_id):
    """Collect optional changes and patch an item."""
    payload = {}
    price = input("New price (blank to keep): ").strip()
    stock = input("New stock (blank to keep): ").strip()
    name = input("New name (blank to keep): ").strip()
    if price:
        payload["price"] = float(price)
    if stock:
        payload["stock"] = int(stock)
    if name:
        payload["name"] = name
    print_result(*request_api("PATCH", base_url, f"/inventory/{item_id}", payload=payload))


def delete_item(base_url, item_id):
    """Delete an item after a confirmation prompt."""
    confirmation = input(f"Delete item {item_id}? type yes to confirm: ").strip().lower()
    if confirmation != "yes":
        print("Deletion cancelled.")
        return
    print_result(*request_api("DELETE", base_url, f"/inventory/{item_id}"))


def search_external(base_url, query):
    """Search OpenFoodFacts through the Flask helper route."""
    print_result(*request_api("GET", base_url, "/external-products/search", params={"query": query}))


def build_parser():
    """Create a non-interactive command parser for scripts and demonstrations."""
    parser = argparse.ArgumentParser(description="Inventory API command-line client")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list")
    view = subparsers.add_parser("view")
    view.add_argument("item_id", type=int)
    subparsers.add_parser("add")
    update = subparsers.add_parser("update")
    update.add_argument("item_id", type=int)
    delete = subparsers.add_parser("delete")
    delete.add_argument("item_id", type=int)
    search = subparsers.add_parser("search")
    search.add_argument("query")
    return parser


def interactive_menu(base_url):
    """Run a menu loop suitable for a human user."""
    actions = {
        "1": lambda: list_items(base_url),
        "2": lambda: view_item(base_url, int(input("Item ID: "))),
        "3": lambda: add_item(base_url),
        "4": lambda: update_item(base_url, int(input("Item ID: "))),
        "5": lambda: delete_item(base_url, int(input("Item ID: "))),
        "6": lambda: search_external(base_url, input("Barcode or name: ")),
    }
    while True:
        print("\n1 List  2 View  3 Add  4 Update  5 Delete  6 Search  0 Exit")
        choice = input("Choose an action: ").strip()
        if choice == "0":
            print("Goodbye.")
            return
        action = actions.get(choice)
        if action is None:
            print("Invalid menu choice.")
            continue
        try:
            action()
        except (ValueError, EOFError) as error:
            print(f"Input error: {error}")


def main(argv=None):
    """CLI entry point supporting commands and the interactive menu."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        interactive_menu(args.base_url)
    elif args.command == "list":
        list_items(args.base_url)
    elif args.command == "view":
        view_item(args.base_url, args.item_id)
    elif args.command == "add":
        add_item(args.base_url)
    elif args.command == "update":
        update_item(args.base_url, args.item_id)
    elif args.command == "delete":
        delete_item(args.base_url, args.item_id)
    elif args.command == "search":
        search_external(args.base_url, args.query)
    return 0


if __name__ == "__main__":
    sys.exit(main())
