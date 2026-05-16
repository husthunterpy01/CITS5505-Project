import pytest
from flask import Flask

from app import app


@pytest.fixture
def flask_app_ctx():
    """Push the real app context so Model.query can be inspected/patched safely."""
    with app.app_context():
        yield


@pytest.fixture
def app_ctx():
    """Minimal Flask request context for session-dependent tests (no DB)."""
    mini = Flask(__name__)
    mini.secret_key = "test-secret"
    with mini.test_request_context():
        yield mini
