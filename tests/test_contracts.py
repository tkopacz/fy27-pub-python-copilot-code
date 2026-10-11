import pytest

from triage.contracts import Classification, InvalidClassification
from triage.providers import DemoClassifier
from triage.service import triage_report


VALID = {"category": "product", "priority": "P2", "sentiment": "negative", "rationale": "Brak produktu."}


def test_valid_classification():
    assert Classification.from_payload(VALID).category == "product"


@pytest.mark.parametrize("payload", [
    [], None, "{}", {}, {**VALID, "category": "invented"},
    {**VALID, "priority": "P0"}, {**VALID, "sentiment": "angry"},
    {**VALID, "rationale": ""}, {**VALID, "rationale": "x" * 501},
    {**VALID, "extra": 1}, {**VALID, "category": []},
])
def test_invalid_model_output(payload):
    with pytest.raises(InvalidClassification):
        Classification.from_payload(payload)


def test_model_rationale_is_redacted_too():
    class PersonalDataClassifier(DemoClassifier):
        def classify(self, text):
            return {**VALID, "rationale": "Kontakt klient@example.test."}

    result = triage_report("Brak produktu.", "store-001", PersonalDataClassifier())
    assert result["rationale"] == "Kontakt [EMAIL]."
    assert result["jira_draft"] is not None
    assert "klient@example.test" not in result["jira_draft"]["description"]
