import json
import tempfile
import unittest
from pathlib import Path

from check_csv import main, validate_csv


SKILL_ROOT = Path(__file__).resolve().parent.parent


class CsvQualityTests(unittest.TestCase):
    def test_bundled_examples(self) -> None:
        for name, status, rows, valid, total, records in (
            ("valid.csv", "PASS", 2, 2, "77.50", []),
            ("invalid.csv", "FAIL", 4, 2, "31.00", [3, 4]),
        ):
            with self.subTest(name=name):
                report = validate_csv(SKILL_ROOT / "examples" / name)
                self.assertEqual(report["status"], status)
                self.assertEqual(report["rows"], rows)
                self.assertEqual(report["valid_rows"], valid)
                self.assertEqual(report["invalid_rows"], rows - valid)
                self.assertEqual(report["valid_total"], total)
                self.assertEqual([issue["row"] for issue in report["issues"]], records)
                self.assertEqual(set(report), {
                    "schema_version", "status", "rows", "valid_rows",
                    "invalid_rows", "valid_total", "issues",
                })

    def test_validation_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "input.csv"
            for quantity, price, valid in (
                ("1", "0", True), ("9999", "0.01", True),
                ("0", "1", False), ("10000", "1", False),
                ("01", "1", False), ("1", "-1", False),
                ("1", "1.001", False), ("1", "Infinity", False),
                ("1", "1e2", False),
            ):
                with self.subTest(quantity=quantity, price=price):
                    source.write_text(
                        f"item,quantity,unit_price\nExample,{quantity},{price}\n",
                        encoding="utf-8",
                    )
                    self.assertEqual(validate_csv(source)["valid_rows"], int(valid))
            source.write_text(
                "item,quantity,unit_price\n,1,2\nExample,1\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [issue["field"] for issue in validate_csv(source)["issues"]],
                ["item", "row"],
            )

    def test_decimal_and_bom(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "input.csv"
            source.write_text(
                "item,quantity,unit_price\nExample,3,0.10\nExample,1,0.20\n",
                encoding="utf-8-sig",
            )
            self.assertEqual(validate_csv(source)["valid_total"], "0.50")

    def test_cli_exit_codes_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, code in (("valid.csv", 0), ("invalid.csv", 1)):
                output = root / f"{name}.json"
                source = SKILL_ROOT / "examples" / name
                before = source.read_bytes()
                arguments = ["--input", str(source), "--output", str(output)]
                self.assertEqual(main(arguments), code)
                saved = output.read_bytes()
                self.assertEqual(json.loads(saved)["status"], "PASS" if code == 0 else "FAIL")
                self.assertEqual(main(arguments), 2)
                self.assertEqual(output.read_bytes(), saved)
                self.assertEqual(source.read_bytes(), before)

    def test_blocked_inputs_create_no_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, output = root / "input.csv", root / "report.json"
            arguments = ["--input", str(source), "--output", str(output)]
            self.assertEqual(main(arguments), 2)
            for content in (
                "", "item,quantity,unit_price\n", "wrong,header\nExample,1\n",
                'item,quantity,unit_price\n"unclosed,1,2\n',
            ):
                with self.subTest(content=content):
                    source.write_text(content, encoding="utf-8")
                    self.assertEqual(main(arguments), 2)
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
