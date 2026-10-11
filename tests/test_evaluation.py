import json
from pathlib import Path

import pytest

from triage.contracts import CATEGORIES
from triage.evaluate import evaluate, load_cases
from triage.providers import DemoClassifier


ROOT = Path(__file__).resolve().parent.parent


def test_dataset_has_balanced_categories():
    cases = load_cases(ROOT / "starter" / "data" / "evaluation.json")
    assert len(cases) == 25
    assert all(sum(c["category"] == category for c in cases) == 5 for category in CATEGORIES)


def test_perfect_predictions_score_one():
    texts = ["Zamówienie", "Dostawa", "Obsługa", "Produkt", "Halo"]
    cases = [
        {"id": str(i), "text": text, "category": category, "priority": "P3" if category == "other" else "P2"}
        for i, (text, category) in enumerate(zip(texts, CATEGORIES))
    ]
    result = evaluate(cases, DemoClassifier())
    assert result["macro_f1"] == 1.0
    assert result["priority_accuracy"] == 1.0
    assert result["mismatches"] == []


def test_macro_f1_uses_false_positives_and_false_negatives():
    cases = [
        {"id": category, "text": "?", "category": category, "priority": "P3"}
        for category in CATEGORIES
    ]
    result = evaluate(cases, DemoClassifier())
    assert result["macro_f1"] == pytest.approx(1 / 15)
    assert result["per_category_f1"]["other"] == pytest.approx(1 / 3)
    assert len(result["mismatches"]) == 4


def test_empty_evaluation_is_an_error():
    with pytest.raises(ValueError, match="empty"):
        evaluate([], DemoClassifier())


def test_dataset_missing_categories_is_an_error(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps([{"id": "1", "text": "?", "category": "other", "priority": "P3"}]))
    with pytest.raises(ValueError, match="every category"):
        load_cases(path)


def test_challenge_dataset_is_well_formed():
    assert len(load_cases(ROOT / "starter" / "data" / "challenge.json")) == 6
