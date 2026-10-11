from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import unquote, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


def export(source: Path, destination: Path, *options: str) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL, "PowerShell is required to test the participant exporter"
    return subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(source / "scripts" / "export-participant.ps1"),
            "-Destination",
            str(destination),
            *options,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def source(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    scripts = source / "scripts"
    scripts.mkdir(parents=True)
    shutil.copyfile(ROOT / "scripts" / "export-participant.ps1", scripts / "export-participant.ps1")
    (scripts / "participant-files.txt").write_text("lab.md\nissues\\iss001.md\n", encoding="utf-8")
    (source / "lab.md").write_text("Participant instructions", encoding="utf-8")
    (source / "issues").mkdir()
    (source / "issues" / "iss001.md").write_text("Synthetic work item", encoding="utf-8")
    return source


def test_real_package_contains_only_selected_files(tmp_path: Path) -> None:
    destination = tmp_path / "participant"
    result = export(ROOT, destination)
    assert result.returncode == 0, result.stdout + result.stderr
    expected = {
        Path(line)
        for line in (ROOT / "scripts" / "participant-files.txt").read_text().splitlines()
        if line
    }
    actual = {path.relative_to(destination) for path in destination.rglob("*") if path.is_file()}
    assert actual == expected
    for relative in expected:
        assert (destination / relative).read_bytes() == (ROOT / relative).read_bytes()
    for document in destination.rglob("*.md"):
        for link in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", document.read_text(encoding="utf-8")):
            url = urlsplit(link)
            if not url.scheme and url.path:
                assert (document.parent / unquote(url.path)).exists(), f"{document}: {link}"
    assert {path.name for path in (destination / "issues").glob("*.md")} == {
        f"iss{number:03}.md" for number in range(1, 11)
    }
    for excluded in (
        ".env", ".git", ".github", ".venv", "reports", "lab-speaker.md",
        "lab-speaker.pdf", "lab.pdf", "demo.md", "README.md", "scripts\\demo",
        "triage\\templates\\AGENTS.md",
    ):
        assert not (destination / excluded).exists()


def test_existing_destination_is_untouched(source: Path, tmp_path: Path) -> None:
    destination = tmp_path / "existing"
    destination.mkdir()
    sentinel = destination / "keep.txt"
    sentinel.write_text("Existing work", encoding="utf-8")
    result = export(source, destination)
    assert result.returncode != 0
    assert "already exists" in result.stderr
    assert list(destination.iterdir()) == [sentinel]
    assert sentinel.read_text() == "Existing work"


def test_destination_inside_source_is_rejected(source: Path) -> None:
    destination = source / "participant"
    result = export(source, destination)
    assert result.returncode != 0
    assert "outside the source" in result.stderr
    assert not destination.exists()


def test_missing_input_fails_before_copying(source: Path, tmp_path: Path) -> None:
    (source / "issues" / "iss001.md").unlink()
    destination = tmp_path / "participant"
    result = export(source, destination)
    assert result.returncode != 0
    assert "Required participant file is missing" in result.stderr
    assert not destination.exists()


@pytest.mark.parametrize("entry", ["..\\outside.txt", "C:\\outside.txt", "issues\\*.md"])
def test_invalid_manifest_path_is_rejected(source: Path, tmp_path: Path, entry: str) -> None:
    (source / "scripts" / "participant-files.txt").write_text(entry + "\n", encoding="utf-8")
    destination = tmp_path / "participant"
    result = export(source, destination)
    assert result.returncode != 0
    assert "Invalid relative path" in result.stderr
    assert not destination.exists()


def test_pdf_is_explicit_and_required_when_requested(source: Path, tmp_path: Path) -> None:
    destination = tmp_path / "participant"
    result = export(source, destination, "-IncludePdf")
    assert result.returncode != 0
    assert not destination.exists()
    (source / "lab.pdf").write_bytes(b"Synthetic PDF fixture")
    (source / "lab-speaker.pdf").write_bytes(b"Private fixture")
    result = export(source, destination, "-IncludePdf")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (destination / "lab.pdf").read_bytes() == b"Synthetic PDF fixture"
    assert not (destination / "lab-speaker.pdf").exists()


def test_unlisted_files_are_not_copied(source: Path, tmp_path: Path) -> None:
    (source / ".env").write_text("SYNTHETIC_ONLY=do-not-copy", encoding="utf-8")
    (source / "issues" / "private.md").write_text("Not for distribution", encoding="utf-8")
    destination = tmp_path / "participant"
    result = export(source, destination)
    assert result.returncode == 0, result.stdout + result.stderr
    assert sorted(str(path.relative_to(destination)) for path in destination.rglob("*") if path.is_file()) == [
        "issues\\iss001.md", "lab.md",
    ]


@pytest.mark.parametrize("location", ["source", "destination"])
def test_junctions_are_rejected(source: Path, tmp_path: Path, location: str) -> None:
    assert POWERSHELL
    external = tmp_path / "external"
    external.mkdir()
    if location == "source":
        junction = source / "issues"
        (junction / "iss001.md").unlink()
        junction.rmdir()
        (external / "iss001.md").write_text("Must not be followed", encoding="utf-8")
        destination = tmp_path / "participant"
    else:
        junction = tmp_path / "alias"
        destination = junction / "participant"
    quoted_junction = str(junction).replace("'", "''")
    quoted_external = str(external).replace("'", "''")
    result = subprocess.run(
        [
            POWERSHELL, "-NoProfile", "-NonInteractive", "-Command",
            f"New-Item -ItemType Junction -Path '{quoted_junction}' -Target '{quoted_external}'",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    try:
        result = export(source, destination)
        assert result.returncode != 0
        assert "Links and junctions are not supported" in result.stderr
        assert not destination.exists()
    finally:
        junction.rmdir()
