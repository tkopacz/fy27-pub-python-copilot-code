import argparse
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile


EXPECTED_FAILURE = (
    "tests.test_privacy.test_spaced_phone_is_redacted_before_model_and_export"
)


def readiness(junit: Path, commit: str) -> dict:
    cases = list(ET.parse(junit).getroot().iter("testcase"))
    if not cases:
        raise ValueError("JUnit contains no test cases.")
    failures = []
    for case in cases:
        name = f"{case.get('classname')}.{case.get('name')}"
        if case.find("error") is not None or case.find("skipped") is not None:
            raise ValueError(f"Blocked: error or skipped test: {name}")
        if case.find("failure") is not None:
            failures.append(name)
    if failures != [EXPECTED_FAILURE]:
        raise ValueError(f"Expected exactly the starter failure; observed: {failures}")
    return {
        "commit": commit,
        "gate": "STARTER_DEMO_ONLY",
        "passed": len(cases) - 1,
        "failed": 1,
        "failures": failures,
        "mode": "demo",
        "synthetic_data_only": True,
        "lab_acceptance": "NOT_PASSED",
    }


def package(root: Path, dependencies: Path, output: Path, commit: str) -> None:
    if not dependencies.is_dir() or not (dependencies / "gunicorn").is_dir():
        raise ValueError("Missing Linux dependencies, including Gunicorn.")
    files = []
    for source in (root / "triage").rglob("*"):
        if source.is_file() and source.suffix in {".py", ".html", ".css", ".js", ".svg"}:
            if "__pycache__" not in source.parts:
                files.append((source, source.relative_to(root).as_posix()))
    for source in dependencies.rglob("*"):
        relative = source.relative_to(dependencies)
        if source.is_file() and not (
            "__pycache__" in relative.parts
            or relative.parts[0] == "bin"
            or source.suffix in {".pyc", ".pyo"}
        ):
            files.append((source, ".python_packages/lib/site-packages/" + relative.as_posix()))
    if not any(name == "triage/app.py" for _, name in files):
        raise ValueError("Missing triage/app.py.")
    files.append((root / "scripts" / "demo" / "wsgi.py", "azure_demo_wsgi.py"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for source, name in sorted(files, key=lambda item: item[1]):
            if source.is_symlink():
                raise ValueError(f"Refusing a symbolic link: {source}")
            archive.write(source, name)
        archive.writestr(
            "triage/static/deployment.json",
            json.dumps({"commit": commit, "mode": "demo", "scope": "synthetic-demo-only"}),
        )


def request_json(url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def smoke(base_url: str, commit: str, attempts: int = 30, delay: float = 10) -> dict:
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(".azurewebsites.net")
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ValueError("Expected an HTTPS Azure App Service origin, without credentials.")
    if attempts < 1 or delay < 0:
        raise ValueError("Invalid retry settings.")
    base_url = base_url.rstrip("/")
    for attempt in range(1, attempts + 1):
        try:
            status, health = request_json(base_url + "/health")
            release_status, release = request_json(base_url + "/static/deployment.json")
            if (
                status == 200
                and health == {
                    "status": "ok", "mode": "demo", "model_connectivity": "not_checked"
                }
                and release_status == 200
                and release.get("commit") == commit
                and release.get("mode") == "demo"
            ):
                break
            reason = f"Health/release not ready: HTTP {status}/{release_status}"
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            reason = f"{type(error).__name__}: {error}"
        print(f"Readiness attempt {attempt}/{attempts}: {reason}", file=sys.stderr)
        if attempt == attempts:
            raise RuntimeError("Azure deployment did not become ready: " + reason)
        time.sleep(delay)
    with urlopen(base_url + "/", timeout=30) as response:
        html = response.read().decode("utf-8")
        if response.status != 200 or "to nie jest LLM" not in html:
            raise RuntimeError("Home page does not disclose the demo mode.")
    status, result = request_json(base_url + "/api/triage", {
        "store_id": "store-001",
        "text": "Obsługa super, ale nie mogę zamówić towaru.",
    })
    expected = {
        "store_id": "store-001", "category": "order", "priority": "P1",
        "sentiment": "mixed", "team": "commerce-support",
        "review_status": "draft_ready", "mode": "demo",
    }
    if status != 200 or any(result.get(key) != value for key, value in expected.items()):
        raise RuntimeError("Synthetic triage does not match the starter contract.")
    if not isinstance(result.get("jira_draft"), dict) or result["jira_draft"].get("project") != "DEMO":
        raise RuntimeError("Missing the local DEMO draft.")
    status, unclear = request_json(base_url + "/api/triage", {
        "store_id": "store-001", "text": "Proszę o kontakt.",
    })
    if status != 200 or unclear.get("review_status") != "manual_review" or unclear.get("jira_draft") is not None:
        raise RuntimeError("Unclear input does not require manual review.")
    status, invalid = request_json(base_url + "/api/triage", {"store_id": "invalid", "text": "Test"})
    if status != 400 or "error" not in invalid:
        raise RuntimeError("Invalid input was not explicitly rejected.")
    return {
        "url": base_url, "commit": commit, "mode": "demo",
        "checks": ["health", "release_commit", "home", "draft", "manual_review", "invalid_400"],
        "result": "PASS", "lab_acceptance": "NOT_PASSED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence and packaging for the separate Azure demo.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evidence = subparsers.add_parser("readiness")
    evidence.add_argument("--junit", type=Path, required=True)
    evidence.add_argument("--output", type=Path, required=True)
    build = subparsers.add_parser("package")
    build.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    build.add_argument("--dependencies", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    check = subparsers.add_parser("smoke")
    check.add_argument("--url", required=True)
    check.add_argument("--output", type=Path, required=True)
    for command in (evidence, build, check):
        command.add_argument("--commit", required=True)
    args = parser.parse_args()
    if args.command == "package":
        package(args.root, args.dependencies, args.output, args.commit)
        return
    result = (
        readiness(args.junit, args.commit) if args.command == "readiness"
        else smoke(args.url, args.commit)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
