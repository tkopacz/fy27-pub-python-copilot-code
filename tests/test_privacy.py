import pytest

from triage.privacy import redact
from triage.providers import DemoClassifier
from triage.service import triage_report


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("klient@example.test", "[EMAIL]"),
        ("500600700", "[PHONE]"),
        ("+48500600700", "[PHONE]"),
        ("00000000000", "[PESEL]"),
        ("store-001", "store-001"),
        ("Dostawa 20 sztuk.", "Dostawa 20 sztuk."),
    ],
)
def test_supported_redaction(source, expected):
    assert redact(source) == expected


def test_redaction_is_idempotent():
    text = "Kontakt klient@example.test, +48500600700."
    assert redact(redact(text)) == redact(text)


def test_spaced_phone_is_redacted_before_model_and_export():
    class RecordingClassifier(DemoClassifier):
        received = ""

        def classify(self, text):
            self.received = text
            return super().classify(text)

    provider = RecordingClassifier()
    result = triage_report(
        "Brak całej dostawy. Kontakt +48 500 600 700.",
        "store-001",
        provider,
    )
    assert provider.received == "Brak całej dostawy. Kontakt [PHONE]."
    assert result["sanitized_text"] == provider.received
    assert result["jira_draft"] is not None
    assert "+48 500 600 700" not in result["jira_draft"]["description"]
