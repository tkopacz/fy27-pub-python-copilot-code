import argparse
import json
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv

from triage.contracts import CATEGORIES
from triage.providers import Classifier, build_classifier
from triage.service import triage_report


ROOT = Path(__file__).resolve().parent.parent


class Case(TypedDict):
    id: str
    text: str
    category: str
    priority: str


def load_cases(path: Path) -> list[Case]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("Evaluation dataset must be a nonempty list.")
    seen = set()
    for case in payload:
        if not isinstance(case, dict) or set(case) != {"id", "text", "category", "priority"}:
            raise ValueError("Invalid evaluation case shape.")
        if not all(isinstance(value, str) and value.strip() for value in case.values()):
            raise ValueError("Evaluation case values must be nonempty strings.")
        if case["id"] in seen or case["category"] not in CATEGORIES or case["priority"] not in ("P1", "P2", "P3"):
            raise ValueError("Invalid or duplicate evaluation case.")
        seen.add(case["id"])
    if {case["category"] for case in payload} != set(CATEGORIES):
        raise ValueError("Evaluation must cover every category.")
    return payload


def evaluate(cases: list[Case], classifier: Classifier) -> dict:
    if not cases:
        raise ValueError("Cannot evaluate an empty dataset.")
    predictions = [
        triage_report(case["text"], "store-001", classifier) for case in cases
    ]
    per_category = {}
    for category in CATEGORIES:
        tp = sum(c["category"] == category and p["category"] == category for c, p in zip(cases, predictions))
        fp = sum(c["category"] != category and p["category"] == category for c, p in zip(cases, predictions))
        fn = sum(c["category"] == category and p["category"] != category for c, p in zip(cases, predictions))
        denominator = 2 * tp + fp + fn
        per_category[category] = 2 * tp / denominator if denominator else 0.0
    return {
        "mode": classifier.mode,
        "cases": len(cases),
        "macro_f1": sum(per_category.values()) / len(CATEGORIES),
        "per_category_f1": per_category,
        "priority_accuracy": sum(c["priority"] == p["priority"] for c, p in zip(cases, predictions)) / len(cases),
        "manual_review_count": sum(p["review_status"] == "manual_review" for p in predictions),
        "mismatches": [
            {
                "id": c["id"],
                "expected_category": c["category"],
                "actual_category": p["category"],
                "expected_priority": c["priority"],
                "actual_priority": p["priority"],
            }
            for c, p in zip(cases, predictions)
            if c["category"] != p["category"] or c["priority"] != p["priority"]
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=ROOT / "starter" / "data" / "evaluation.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-macro-f1", type=float)
    args = parser.parse_args()
    if args.min_macro_f1 is not None and not 0 <= args.min_macro_f1 <= 1:
        parser.error("--min-macro-f1 must be between 0 and 1")
    load_dotenv(ROOT / ".env", override=False)
    report = evaluate(load_cases(args.dataset), build_classifier())
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.min_macro_f1 is not None and report["macro_f1"] < args.min_macro_f1:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
