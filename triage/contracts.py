from dataclasses import dataclass
from typing import Literal, TypedDict


CATEGORIES = ("order", "delivery", "store_service", "product", "other")
PRIORITIES = ("P1", "P2", "P3")
SENTIMENTS = ("positive", "neutral", "negative", "mixed")
TEAMS = {
    "order": "commerce-support",
    "delivery": "logistics",
    "store_service": "store-operations",
    "product": "quality",
    "other": "manual-triage",
}


class InvalidClassification(ValueError):
    pass


class JiraDraft(TypedDict):
    project: str
    issuetype: str
    summary: str
    description: str
    priority: str
    team: str


class TriageResult(TypedDict):
    store_id: str
    sanitized_text: str
    category: str
    priority: str
    sentiment: str
    rationale: str
    team: str
    review_status: Literal["draft_ready", "manual_review"]
    jira_draft: JiraDraft | None
    mode: str


@dataclass(frozen=True)
class Classification:
    category: str
    priority: str
    sentiment: str
    rationale: str

    @classmethod
    def from_payload(cls, payload: object) -> "Classification":
        if not isinstance(payload, dict):
            raise InvalidClassification("Model output must be a JSON object.")
        if set(payload) != {"category", "priority", "sentiment", "rationale"}:
            raise InvalidClassification("Model output has incorrect fields.")
        for field, allowed in (
            ("category", CATEGORIES),
            ("priority", PRIORITIES),
            ("sentiment", SENTIMENTS),
        ):
            if not isinstance(payload[field], str) or payload[field] not in allowed:
                raise InvalidClassification(f"Invalid {field} in model output.")
        rationale = payload["rationale"]
        if not isinstance(rationale, str) or not 1 <= len(rationale.strip()) <= 500:
            raise InvalidClassification("Rationale must contain 1-500 characters.")
        return cls(
            category=payload["category"],
            priority=payload["priority"],
            sentiment=payload["sentiment"],
            rationale=rationale.strip(),
        )
