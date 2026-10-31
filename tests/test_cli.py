"""Tests for the command-line client without requiring a running server."""

from unittest.mock import Mock, patch

import cli


def fake_response(payload, status_code=200):
    """Create a small response object for the CLI request helper."""
    response = Mock()
    response.ok = 200 <= status_code < 400
    response.status_code = status_code
    response.json.return_value = payload
    response.text = ""
    return response


def test_request_api_success():
    payload = [{"id": 1, "name": "Tea"}]
    with patch("cli.requests.request", return_value=fake_response(payload)) as mocked:
        success, data = cli.request_api("GET", "http://api", "/inventory")
    assert success is True
    assert data == payload
    mocked.assert_called_once_with("GET", "http://api/inventory", json=None, params=None, timeout=10)


def test_request_api_http_error():
    with patch("cli.requests.request", return_value=fake_response({"error": "missing"}, 404)):
        success, data = cli.request_api("GET", "http://api", "/inventory/9")
    assert success is False
    assert data["error"] == "missing"


def test_request_api_network_error():
    with patch("cli.requests.request", side_effect=cli.requests.RequestException("offline")):
        success, data = cli.request_api("GET", "http://api", "/health")
    assert success is False
    assert "could not contact" in data["error"].lower()


def test_list_items_calls_inventory_endpoint():
    with patch("cli.request_api", return_value=(True, [])) as request_api:
        cli.list_items("http://api")
    request_api.assert_called_once_with("GET", "http://api", "/inventory")


def test_view_item_calls_detail_endpoint():
    with patch("cli.request_api", return_value=(True, {})) as request_api:
        cli.view_item("http://api", 4)
    request_api.assert_called_once_with("GET", "http://api", "/inventory/4")


def test_search_external_calls_search_endpoint():
    with patch("cli.request_api", return_value=(True, {})) as request_api:
        cli.search_external("http://api", "milk")
    request_api.assert_called_once_with(
        "GET", "http://api", "/external-products/search", params={"query": "milk"}
    )


def test_build_parser_supports_view_command():
    parser = cli.build_parser()
    args = parser.parse_args(["view", "12"])
    assert args.command == "view"
    assert args.item_id == 12


def test_build_parser_supports_search_command():
    parser = cli.build_parser()
    args = parser.parse_args(["--base-url", "http://demo", "search", "tea"])
    assert args.base_url == "http://demo"
    assert args.query == "tea"


def test_delete_cancel_does_not_call_api():
    with patch("builtins.input", return_value="no"), patch("cli.request_api") as request_api:
        cli.delete_item("http://api", 1)
    request_api.assert_not_called()
