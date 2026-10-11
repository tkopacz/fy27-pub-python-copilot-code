import pytest

from triage.app import create_app
from triage.providers import DemoClassifier, ProviderError


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "mode": "demo", "model_connectivity": "not_checked"}


def test_home_discloses_demo_and_no_jira_write(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "to nie jest LLM" in response.get_data(as_text=True)
    assert "nic nie trafia do Jiry" in response.get_data(as_text=True)


def test_actionable_report_has_draft(client):
    response = client.post("/api/triage", json={
        "text": "Obsługa super, ale nie mogę zamówić towaru.",
        "store_id": "store-001",
    })
    assert response.status_code == 200
    body = response.json
    assert set(body) == {
        "store_id", "sanitized_text", "category", "priority", "sentiment",
        "rationale", "team", "review_status", "jira_draft", "mode",
    }
    assert body["category"] == "order"
    assert body["priority"] == "P1"
    assert body["sentiment"] == "mixed"
    assert body["team"] == "commerce-support"
    assert body["review_status"] == "draft_ready"
    assert body["jira_draft"]["project"] == "DEMO"


def test_unclear_report_requires_manual_review(client):
    body = client.post("/api/triage", json={"text": "Proszę o kontakt.", "store_id": "store-001"}).json
    assert body["category"] == "other"
    assert body["review_status"] == "manual_review"
    assert body["jira_draft"] is None


@pytest.mark.parametrize("payload", [
    None, [], {}, {"text": "Hello"}, {"text": "", "store_id": "store-001"},
    {"text": "  ", "store_id": "store-001"},
    {"text": 42, "store_id": "store-001"},
    {"text": "x" * 4001, "store_id": "store-001"},
    {"text": "Hello", "store_id": "Jan Kowalski"},
    {"text": "Hello", "store_id": "store-001", "extra": True},
])
def test_invalid_input(client, payload):
    import json

    response = client.post("/api/triage", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.json


def test_malformed_json(client):
    response = client.post("/api/triage", data="{broken", content_type="application/json")
    assert response.status_code == 400
    assert response.json["error"] == "Invalid JSON body."


def test_wrong_content_type(client):
    assert client.post("/api/triage", data="hello").status_code == 415


def test_oversized_request(client):
    response = client.post("/api/triage", data="x" * 20_000, content_type="application/json")
    assert response.status_code == 413


def test_model_error_is_not_replaced_by_demo_result(caplog):
    class BrokenClassifier(DemoClassifier):
        def classify(self, text):
            raise ProviderError("Endpoint unavailable.")

    client = create_app(BrokenClassifier()).test_client()
    response = client.post("/api/triage", json={"text": "Private synthetic input.", "store_id": "store-001"})
    assert response.status_code == 502
    assert response.json == {"error": "Endpoint unavailable."}
    assert "ProviderError" in caplog.text
    assert "Private synthetic input" not in caplog.text


def test_invalid_model_category_is_rejected():
    class InvalidClassifier(DemoClassifier):
        def classify(self, text):
            return {"category": "executive", "priority": "P1", "sentiment": "neutral", "rationale": "Test"}

    client = create_app(InvalidClassifier()).test_client()
    response = client.post("/api/triage", json={"text": "Test", "store_id": "store-001"})
    assert response.status_code == 502
    assert "jira_draft" not in response.json
