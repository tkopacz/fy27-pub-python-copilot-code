"""Tworzy raport bramek odbioru na podstawie dowodów, nie deklaracji agenta."""

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path.name}")
    return value


def exit_code(path: Path) -> int:
    code = read_json(path)["exit_code"]
    if type(code) is not int or code < 0:
        raise ValueError(f"Invalid exit code: {path.name}")
    return code


def summarize(directory: Path) -> dict:
    tests_exit = exit_code(directory / "tests-exit.json")
    metrics_exit = exit_code(directory / "metrics-exit.json")
    if tests_exit > 1 or metrics_exit != 0:
        raise ValueError("A worker could not complete its evidence collection.")
    root = ElementTree.parse(directory / "tests.xml").getroot()
    suites = list(root.iter("testsuite"))
    if not suites:
        raise ValueError("JUnit report contains no test suites.")
    counts = {
        key: sum(int(suite.attrib[key]) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    if any(value < 0 for value in counts.values()) or counts["tests"] == 0:
        raise ValueError("JUnit report contains invalid or empty counts.")
    unsuccessful = counts["failures"] + counts["errors"] + counts["skipped"]
    if unsuccessful > counts["tests"]:
        raise ValueError("JUnit counts are inconsistent.")
    counts["passed"] = counts["tests"] - unsuccessful
    evaluation = read_json(directory / "evaluation.json")
    if evaluation["mode"] != "demo":
        raise ValueError("This workflow requires demo evidence.")
    if type(evaluation["cases"]) is not int or evaluation["cases"] <= 0:
        raise ValueError("Evaluation contains no cases.")
    for key in ("macro_f1", "priority_accuracy"):
        value = evaluation[key]
        if type(value) not in (int, float) or not 0 <= value <= 1:
            raise ValueError(f"Invalid metric: {key}")
    tests_pass = tests_exit == 0 and unsuccessful == 0
    metrics_pass = metrics_exit == 0 and all(
        evaluation[key] >= 0.90 for key in ("macro_f1", "priority_accuracy")
    )
    return {
        "schema_version": 1,
        "status": "PASS" if tests_pass and metrics_pass else "FAIL",
        "tests": {"status": "PASS" if tests_pass else "FAIL",
                  "exit_code": tests_exit, **counts},
        "metrics": {
            "status": "PASS" if metrics_pass else "FAIL",
            "exit_code": metrics_exit,
            "mode": evaluation["mode"],
            "cases": evaluation["cases"],
            "macro_f1": evaluation["macro_f1"],
            "priority_accuracy": evaluation["priority_accuracy"],
            "threshold": 0.90,
        },
        "acceptance": {f"AC-{number:02}": "NOT_VERIFIED" for number in range(1, 12)},
        "limitations": [
            "Gate PASS is not acceptance of all workshop criteria.",
            "Inspect assertions for AC-01 and new behavior; compare baseline for AC-10.",
            "Usability and TUI need separate evidence; no live inference was tested.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-directory", type=Path, required=True)
    args = parser.parse_args()
    output = args.run_directory / "summary.json"
    try:
        if output.exists():
            raise ValueError("Summary already exists. Use a new run directory.")
        report = summarize(args.run_directory)
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0 if report["status"] == "PASS" else 1
    except (OSError, ValueError, KeyError, TypeError, ElementTree.ParseError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
