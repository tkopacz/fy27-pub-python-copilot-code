from triage.contracts import Classification, JiraDraft, TEAMS, TriageResult
from triage.privacy import redact
from triage.providers import Classifier


def triage_report(text: str, store_id: str, classifier: Classifier) -> TriageResult:
    sanitized = redact(text)
    result = Classification.from_payload(classifier.classify(sanitized))
    team = TEAMS[result.category]
    manual_review = result.category == "other"
    rationale = redact(result.rationale)
    draft: JiraDraft | None = None
    if not manual_review:
        draft = {
            "project": "DEMO",
            "issuetype": "Task",
            "summary": f"[{store_id}] {result.category}",
            "description": f"{sanitized}\n\nUzasadnienie: {rationale}",
            "priority": result.priority,
            "team": team,
        }
    return {
        "store_id": store_id,
        "sanitized_text": sanitized,
        "category": result.category,
        "priority": result.priority,
        "sentiment": result.sentiment,
        "rationale": rationale,
        "team": team,
        "review_status": "manual_review" if manual_review else "draft_ready",
        "jira_draft": draft,
        "mode": classifier.mode,
    }
