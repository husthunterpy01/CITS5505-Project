from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.service import productlistingservice as pls


def _make_product(**kwargs):
    defaults = dict(
        product_id=1,
        product_name="Chair",
        description="Nice chair",
        price=25.0,
        category_id=3,
        status="available",
        seller=SimpleNamespace(first_name="Ada", last_name="Lovelace"),
        location=SimpleNamespace(location_name="Crawley"),
        category=SimpleNamespace(category_name="Furniture"),
        images=[],
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _setup_product_query_mock(rows):
    """Patch Product.query so listing helpers return predictable rows."""
    mock_tail = MagicMock()
    mock_tail.all.return_value = rows

    mock_base = MagicMock()
    mock_base.filter.return_value = mock_base
    mock_base.all.return_value = rows
    mock_base.limit.return_value = mock_tail

    chain = MagicMock()
    chain.options.return_value.order_by.return_value = mock_base
    return chain


class TestPrimaryImageForProduct:
    def test_returns_primary_image_url_when_present(self):
        images = [
            SimpleNamespace(image_url="/a.jpg", is_primary=False),
            SimpleNamespace(image_url="/b.jpg", is_primary=True),
        ]
        product = _make_product(images=images)
        assert pls.primary_image_for_product(product, "/default.jpg") == "/b.jpg"

    def test_returns_default_when_no_primary_marked(self):
        images = [
            SimpleNamespace(image_url="/a.jpg", is_primary=False),
        ]
        product = _make_product(images=images)
        assert pls.primary_image_for_product(product, "/default.jpg") == "/default.jpg"

    def test_returns_default_for_empty_image_list(self):
        product = _make_product(images=[])
        assert pls.primary_image_for_product(product, "/default.jpg") == "/default.jpg"


class TestSerializeProductForListing:
    def test_maps_core_fields_and_primary_image(self):
        product = _make_product(
            images=[SimpleNamespace(image_url="/p.jpg", is_primary=True)],
        )
        data = pls.serialize_product_for_listing(product, "/default.jpg")
        assert data["product_id"] == 1
        assert data["title"] == "Chair"
        assert data["description"] == "Nice chair"
        assert data["price"] == 25.0
        assert data["category_name"] == "Furniture"
        assert data["location"] == "Crawley"
        assert data["seller_name"] == "Ada Lovelace"
        assert data["image"] == "/p.jpg"

    def test_description_none_becomes_empty_string(self):
        product = _make_product(description=None)
        data = pls.serialize_product_for_listing(product, "/d.jpg")
        assert data["description"] == ""

    def test_missing_category_and_location_use_none_names(self):
        product = _make_product(category=None, location=None)
        data = pls.serialize_product_for_listing(product, "/d.jpg")
        assert data["category_name"] is None
        assert data["location"] is None


@pytest.mark.usefixtures("flask_app_ctx")
class TestSearchProductsForListing:
    def test_applies_text_category_and_price_filters_and_limit(self):
        rows = [_make_product()]
        chain = _setup_product_query_mock(rows)

        with patch.object(pls.Product, "query", chain):
            out = pls.search_products_for_listing(
                query="chair",
                limit=5,
                category_id=3,
                min_price=10.0,
                max_price=100.0,
            )

        mock_base = chain.options.return_value.order_by.return_value
        assert mock_base.filter.call_count == 4
        mock_base.limit.assert_called_once_with(5)
        assert out is rows

    def test_none_limit_uses_all_instead_of_limit(self):
        rows = [_make_product()]
        chain = _setup_product_query_mock(rows)
        mock_base = chain.options.return_value.order_by.return_value

        with patch.object(pls.Product, "query", chain):
            out = pls.search_products_for_listing(query=None, limit=None)

        mock_base.limit.assert_not_called()
        mock_base.all.assert_called_once()
        assert out is rows

    def test_none_as_search_query_skips_text_filter(self):
        rows = []
        chain = _setup_product_query_mock(rows)
        mock_base = chain.options.return_value.order_by.return_value

        with patch.object(pls.Product, "query", chain):
            pls.search_products_for_listing(query=None, limit=10)

        mock_base.filter.assert_not_called()
