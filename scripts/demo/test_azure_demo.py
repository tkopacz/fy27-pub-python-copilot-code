import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

import pytest


spec = importlib.util.spec_from_file_location("azure_demo", Path(__file__).with_name("azure_demo.py"))
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def junit(tmp_path, extra=""):
    path = tmp_path / "result.xml"
    path.write_text(
        '<testsuites><testsuite>'
        '<testcase classname="tests.test_api" name="test_health"/>'
        '<testcase classname="tests.test_privacy" '
        'name="test_spaced_phone_is_redacted_before_model_and_export">'
        '<failure message="intentional"/></testcase>'
        f'{extra}</testsuite></testsuites>',
        encoding="utf-8",
    )
    return path


def test_readiness_discloses_expected_failure_not_lab_success(tmp_path):
    result = demo.readiness(junit(tmp_path), "abc")
    assert result["gate"] == "STARTER_DEMO_ONLY"
    assert result["failed"] == 1
    assert result["lab_acceptance"] == "NOT_PASSED"


@pytest.mark.parametrize("extra", [
    '<testcase classname="tests.other" name="regression"><failure/></testcase>',
    '<testcase classname="tests.other" name="broken"><error/></testcase>',
    '<testcase classname="tests.other" name="hidden"><skipped/></testcase>',
])
def test_readiness_blocks_regressions_errors_and_skips(tmp_path, extra):
    with pytest.raises(ValueError):
        demo.readiness(junit(tmp_path, extra), "abc")


def test_package_excludes_local_secrets_and_instructor_materials(tmp_path):
    root = tmp_path / "repo"
    (root / "triage" / "templates").mkdir(parents=True)
    (root / "triage" / "app.py").write_text("app = None", encoding="utf-8")
    (root / "triage" / "templates" / "index.html").write_text("demo", encoding="utf-8")
    (root / "scripts" / "demo").mkdir(parents=True)
    (root / "scripts" / "demo" / "wsgi.py").write_text("app = None", encoding="utf-8")
    for path in (root / ".env", root / "lab-speaker.md", root / "triage" / ".env",
                 root / "triage" / "templates" / "AGENTS.md"):
        path.write_text("must not ship", encoding="utf-8")
    dependencies = tmp_path / "dependencies"
    (dependencies / "gunicorn").mkdir(parents=True)
    (dependencies / "gunicorn" / "__init__.py").write_text("", encoding="utf-8")
    output = tmp_path / "app.zip"
    demo.package(root, dependencies, output, "abc")
    with ZipFile(output) as archive:
        assert set(archive.namelist()) == {
            "triage/app.py", "triage/templates/index.html",
            ".python_packages/lib/site-packages/gunicorn/__init__.py",
            "triage/static/deployment.json", "azure_demo_wsgi.py",
        }
        assert json.loads(archive.read("triage/static/deployment.json"))["commit"] == "abc"


def test_smoke_rejects_stale_release_even_when_health_is_green(monkeypatch):
    def response(url, payload=None):
        if url.endswith("/health"):
            return 200, {"status": "ok", "mode": "demo", "model_connectivity": "not_checked"}
        return 200, {"commit": "old", "mode": "demo"}

    monkeypatch.setattr(demo, "request_json", response)
    with pytest.raises(RuntimeError, match="did not become ready"):
        demo.smoke("https://example.azurewebsites.net", "new", attempts=1, delay=0)
