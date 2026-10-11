from pathlib import Path
from collections.abc import Iterator
import re
import shutil
import subprocess
import zlib


ROOT = Path(__file__).resolve().parents[1]


def pdf_streams(pdf: Path) -> Iterator[bytes]:
    data = pdf.read_bytes()
    streams = re.finditer(
        rb"<<([^>]*?/Filter\s*/FlateDecode[^>]*?)>>\s*stream(?:\r\n|\n|\r)",
        data,
        re.DOTALL,
    )
    for stream in streams:
        length = re.search(rb"/Length\s+(\d+)\s*(?=/|$)", stream[1])
        assert length, "Expected a direct stream length in the generated XeLaTeX PDF"
        yield zlib.decompress(data[stream.end():stream.end() + int(length[1])])


def actual_text(pdf: Path) -> str:
    """Read XeLaTeX's ActualText spans without inferring spaces from glyph positions."""
    spans = []
    escapes = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f"}

    def unescape(match: re.Match[bytes]) -> bytes:
        value = match[1]
        if value[:1] in b"01234567":
            return bytes([int(value, 8)])
        return escapes.get(value, value)

    for content in pdf_streams(pdf):
        for match in re.finditer(
            rb"/ActualText\s*(?:<([0-9a-fA-F]+)>|\(((?:\\.|[^\\)])*)\))",
            content,
            re.DOTALL,
        ):
            value = (
                bytes.fromhex(match[1].decode("ascii"))
                if match[1] is not None
                else re.sub(rb"\\([0-7]{1,3}|.)", unescape, match[2], flags=re.DOTALL)
            )
            encoding = "utf-16" if value.startswith((b"\xfe\xff", b"\xff\xfe")) else "latin-1"
            spans.append(value.decode(encoding))
    return "".join(spans)


def test_pdf_preserves_copyable_text_and_link_boundaries(tmp_path: Path) -> None:
    for tool in ("pandoc", "xelatex", "pdftotext"):
        assert shutil.which(tool), f"PDF copy check requires the existing tool: {tool}"

    command = r".\scripts\setup.ps1 -WithLLM"
    arguments = r'.\scripts\test.ps1 -PytestArgs @("tests\test_privacy.py", "-q")'
    continuation = r".\scripts\evaluate.ps1 -Mode demo `"
    opening, closing = "$prompt = @'", "'@"
    prompt = "Przeczytaj źródła i sprawdź wynik. Bez edycji i poleceń powłoki."
    indented = '    return "first  second"'
    target = "starter/copilot/skills/csv-quality/references/input-contract.md"
    source = (
        f"Before [input contract]({target}) after the link.\n\n"
        f"`{command}`\n\n"
        f"```powershell\n{command}\n{arguments}\n{continuation}\n"
        f"  -Output reports\\final-demo.json\n{opening}\n{prompt}\n{closing}\n```\n\n"
        f"```text\n{prompt}\n```\n\n"
        f"```python\ndef example():\n{indented}\n```\n"
    )
    pdf = tmp_path / "copy.pdf"
    result = subprocess.run(
        [
            "pandoc", "--from=markdown-smart", "--standalone",
            "--pdf-engine=xelatex", "--pdf-engine-opt=-disable-installer",
            "--include-in-header", str(ROOT / "scripts" / "pdf-header.tex"),
            "--output", str(pdf),
        ],
        input=source,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    annotations = b"".join(pdf_streams(pdf))
    assert annotations.count(f"/URI({target})".encode("ascii")) == 1, (
        "A one-line link must not spread over the following text or code blocks"
    )

    embedded = actual_text(pdf)
    assert embedded.count(command) == 2, "Inline and fenced commands need literal spaces"
    for line in (arguments, continuation, opening, closing, prompt, indented):
        assert line in embedded, f"Source characters missing from ActualText: {line!r}"

    extracted = subprocess.check_output(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
        encoding="utf-8",
    )
    for line in (command, arguments, continuation, opening, closing, prompt, indented):
        assert line in extracted, f"Copyable text differs from Markdown: {line!r}"
