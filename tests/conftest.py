import pytest

from triage.app import create_app
from triage.providers import DemoClassifier


@pytest.fixture
def client():
    app = create_app(DemoClassifier())
    app.config["TESTING"] = True
    return app.test_client()
