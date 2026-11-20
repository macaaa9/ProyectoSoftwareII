import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "AUTO_CREATE_TABLES": True})
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()
