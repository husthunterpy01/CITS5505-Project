"""Shared pytest fixtures (Flask application context for SQLAlchemy query proxies)."""

import pytest

from app import app


@pytest.fixture
def flask_app_ctx():
    """Push the real app context so Model.query can be inspected/patched safely."""
    with app.app_context():
        yield
