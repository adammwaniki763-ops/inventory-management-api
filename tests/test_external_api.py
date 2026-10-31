"""Unit tests for OpenFoodFacts calls and response normalization."""

from unittest.mock import Mock, patch

import pytest
import requests

from external_api import (
    ExternalAPIError,
    search_by_barcode,
    search_by_name,
    search_open_food_facts,
)


def make_response(payload, status_code=200):
    """Build a small mock response with requests-like behavior."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError("bad status")
    else:
        response.raise_for_status.return_value = None
    return response


def test_barcode_search_normalizes_product():
    payload = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "categories": "Beverages",
            "ingredients_text": "Water, almonds",
            "image_url": "https://example.com/milk.jpg",
        },
    }
    with patch("external_api.requests.get", return_value=make_response(payload)) as mocked:
        results = search_by_barcode("123456")
    assert len(results) == 1
    assert results[0]["name"] == "Organic Almond Milk"
    assert results[0]["brand"] == "Silk"
    assert results[0]["barcode"] == "123456"
    mocked.assert_called_once()


def test_barcode_search_returns_empty_for_unknown_product():
    with patch("external_api.requests.get", return_value=make_response({"status": 0})):
        assert search_by_barcode("000000") == []


def test_name_search_returns_normalized_products():
    payload = {"products": [{"product_name": "Tea", "brands": "Demo"}]}
    with patch("external_api.requests.get", return_value=make_response(payload)) as mocked:
        results = search_by_name("tea")
    assert results[0]["name"] == "Tea"
    assert results[0]["brand"] == "Demo"
    assert mocked.call_args.kwargs["params"]["search_terms"] == "tea"


def test_numeric_query_uses_barcode_lookup():
    with patch("external_api.search_by_barcode", return_value=[{"name": "Milk"}]) as barcode:
        result = search_open_food_facts("12345")
    assert result == [{"name": "Milk"}]
    barcode.assert_called_once_with("12345")


def test_text_query_uses_name_lookup():
    with patch("external_api.search_by_name", return_value=[{"name": "Tea"}]) as name:
        result = search_open_food_facts("tea")
    assert result == [{"name": "Tea"}]
    name.assert_called_once_with("tea")


def test_empty_query_raises_error():
    with pytest.raises(ExternalAPIError):
        search_open_food_facts("   ")


def test_network_error_becomes_external_api_error():
    with patch("external_api.requests.get", side_effect=requests.Timeout("slow")):
        with pytest.raises(ExternalAPIError) as error:
            search_by_name("milk")
    assert "request failed" in str(error.value).lower()


def test_invalid_status_becomes_external_api_error():
    response = make_response({}, status_code=500)
    with patch("external_api.requests.get", return_value=response):
        with pytest.raises(ExternalAPIError):
            search_by_name("milk")
