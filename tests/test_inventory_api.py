"""Tests for every required inventory REST API operation."""

import pytest

from app import create_app
from inventory import reset_inventory


@pytest.fixture()
def client():
    """Create an isolated Flask test client for each test."""
    reset_inventory()
    application = create_app()
    application.config["TESTING"] = True
    with application.test_client() as test_client:
        yield test_client
    reset_inventory()


def test_health_route(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_get_all_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Organic Almond Milk"


def test_get_one_inventory_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_missing_item_returns_404(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"].lower()


def test_create_inventory_item(client):
    payload = {
        "name": "Kenyan Tea",
        "barcode": "123456789",
        "brand": "Highland Tea",
        "category": "Beverages",
        "price": 300,
        "stock": 8,
        "ingredients": "Black tea leaves",
    }
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 3
    assert data["price"] == 300.0
    assert data["stock"] == 8


def test_create_rejects_missing_name(client):
    response = client.post("/inventory", json={"price": 10, "stock": 2})
    assert response.status_code == 400
    assert "name" in response.get_json()["error"]


def test_create_rejects_negative_price(client):
    response = client.post("/inventory", json={"name": "Bad", "price": -2, "stock": 2})
    assert response.status_code == 400
    assert "negative" in response.get_json()["error"]


def test_create_rejects_invalid_json(client):
    response = client.post("/inventory", data="not-json", content_type="text/plain")
    assert response.status_code == 400
    assert "valid json" in response.get_json()["error"].lower()


def test_patch_updates_only_supplied_fields(client):
    response = client.patch("/inventory/1", json={"price": 500, "stock": 7})
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 500.0
    assert data["stock"] == 7
    assert data["name"] == "Organic Almond Milk"


def test_patch_missing_item_returns_404(client):
    response = client.patch("/inventory/999", json={"stock": 1})
    assert response.status_code == 404


def test_patch_empty_payload_returns_400(client):
    response = client.patch("/inventory/1", json={})
    assert response.status_code == 400


def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 200
    assert response.get_json()["item"]["id"] == 2
    remaining = client.get("/inventory").get_json()
    assert len(remaining) == 1


def test_delete_missing_item_returns_404(client):
    response = client.delete("/inventory/1000")
    assert response.status_code == 404


def test_unknown_route_returns_json(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Route not found."


def test_external_search_requires_query(client):
    response = client.get("/external-products/search")
    assert response.status_code == 400
    assert "query" in response.get_json()["error"]
