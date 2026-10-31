"""OpenFoodFacts integration used by the API and CLI.

Network access is isolated in this module so tests can mock requests without
calling the real service. The functions normalize external responses into a
small predictable shape used by the rest of the application.
"""

from urllib.parse import quote

import requests


OPEN_FOOD_FACTS_BY_BARCODE = "https://world.openfoodfacts.org/api/v2/product/{}"
OPEN_FOOD_FACTS_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"


class ExternalAPIError(Exception):
    """Raised when OpenFoodFacts cannot provide a usable response."""


def _normalize_product(product):
    """Convert a large OpenFoodFacts object into useful inventory fields."""
    return {
        "name": product.get("product_name") or product.get("product_name_en") or "Unknown product",
        "barcode": product.get("code", ""),
        "brand": product.get("brands", "Unknown") or "Unknown",
        "category": product.get("categories", "General") or "General",
        "ingredients": product.get("ingredients_text", "") or "",
        "image_url": product.get("image_url", "") or "",
        "source": "OpenFoodFacts",
    }


def _request_json(url, params=None):
    """Perform a GET request and translate network errors to our exception."""
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise ExternalAPIError(f"OpenFoodFacts request failed: {error}") from error
    except ValueError as error:
        raise ExternalAPIError("OpenFoodFacts returned invalid JSON.") from error


def search_by_barcode(barcode):
    """Fetch one product by barcode."""
    clean_barcode = str(barcode).strip()
    if not clean_barcode:
        raise ExternalAPIError("A barcode is required.")
    data = _request_json(OPEN_FOOD_FACTS_BY_BARCODE.format(quote(clean_barcode)))
    if data.get("status") != 1 or not data.get("product"):
        return []
    product = _normalize_product(data["product"])
    product["barcode"] = clean_barcode
    return [product]


def search_by_name(name, page_size=5):
    """Search OpenFoodFacts by product name."""
    clean_name = str(name).strip()
    if not clean_name:
        raise ExternalAPIError("A product name is required.")
    params = {
        "action": "process",
        "search_terms": clean_name,
        "json": "true",
        "page_size": page_size,
        "fields": "code,product_name,product_name_en,brands,categories,ingredients_text,image_url",
    }
    data = _request_json(OPEN_FOOD_FACTS_SEARCH, params=params)
    return [_normalize_product(product) for product in data.get("products", [])]


def search_open_food_facts(query):
    """Choose barcode lookup for digit-only queries, otherwise name search."""
    clean_query = str(query).strip()
    if not clean_query:
        raise ExternalAPIError("A search query is required.")
    if clean_query.isdigit():
        return search_by_barcode(clean_query)
    return search_by_name(clean_query)
