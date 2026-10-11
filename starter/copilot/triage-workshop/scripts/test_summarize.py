import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from summarize import main, summarize


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.write_json("tests-exit.json", {"exit_code": 0})
        self.write_json("metrics-exit.json", {"exit_code": 0})
        self.write_xml()
        self.write_metrics()

    def write_json(self, name, value):
        (self.directory / name).write_text(json.dumps(value), encoding="utf-8")

    def write_xml(self, failures=0, skipped=0, tests=2):
        (self.directory / "tests.xml").write_text(
            f'<testsuites><testsuite tests="{tests}" failures="{failures}" '
            f'errors="0" skipped="{skipped}"/></testsuites>',
            encoding="utf-8",
        )

    def write_metrics(self, f1=0.9, accuracy=0.9, mode="demo"):
        self.write_json("evaluation.json", {
            "mode": mode, "cases": 25,
            "macro_f1": f1, "priority_accuracy": accuracy,
        })

    def test_exact_threshold_passes_without_claiming_acceptance(self):
        report = summarize(self.directory)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["tests"]["passed"], 2)
        self.assertEqual(set(report["acceptance"].values()), {"NOT_VERIFIED"})
        self.assertEqual(len(report["acceptance"]), 11)

    def test_each_metric_must_pass_without_rounding(self):
        for f1, accuracy in ((0.899999999, 1.0), (1.0, 0.899999999)):
            with self.subTest(f1=f1, accuracy=accuracy):
                self.write_metrics(f1=f1, accuracy=accuracy)
                self.assertEqual(summarize(self.directory)["status"], "FAIL")

    def test_test_failure_does_not_mask_successful_measurement(self):
        self.write_json("tests-exit.json", {"exit_code": 1})
        self.write_xml(failures=1)
        report = summarize(self.directory)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["tests"]["failures"], 1)
        self.assertEqual(report["metrics"]["status"], "PASS")

    def test_skipped_test_does_not_pass_gate(self):
        self.write_xml(skipped=1)
        self.assertEqual(summarize(self.directory)["tests"]["status"], "FAIL")

    def test_missing_evidence_is_an_error(self):
        (self.directory / "evaluation.json").unlink()
        with self.assertRaises(FileNotFoundError):
            summarize(self.directory)

    def test_worker_execution_error_is_not_a_quality_failure(self):
        for name, code in (("tests-exit.json", 2), ("metrics-exit.json", 1)):
            with self.subTest(name=name):
                self.write_json(name, {"exit_code": code})
                with self.assertRaises(ValueError):
                    summarize(self.directory)
                self.write_json(name, {"exit_code": 0})

    def test_live_empty_and_invalid_metrics_are_rejected(self):
        for f1, accuracy, mode in (
            (1, 1, "live"), (float("nan"), 1, "demo"),
            (1, True, "demo"), (1.1, 1, "demo"),
        ):
            with self.subTest(f1=f1, accuracy=accuracy, mode=mode):
                self.write_metrics(f1=f1, accuracy=accuracy, mode=mode)
                with self.assertRaises(ValueError):
                    summarize(self.directory)
        self.write_metrics()
        self.write_xml(tests=0)
        with self.assertRaises(ValueError):
            summarize(self.directory)

    def run_main(self):
        with patch("sys.argv", ["summarize.py", "--run-directory", str(self.directory)]):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
                code = main()
        return code, errors.getvalue()

    def test_main_persists_pass_and_fail_with_expected_codes(self):
        output = self.directory / "summary.json"
        for f1, expected_code, status in ((0.9, 0, "PASS"), (0.89, 1, "FAIL")):
            with self.subTest(status=status):
                self.write_metrics(f1=f1)
                code, errors = self.run_main()
                self.assertEqual(code, expected_code)
                self.assertEqual(errors, "")
                self.assertEqual(json.loads(output.read_text())["status"], status)
                output.unlink()

    def test_main_missing_evidence_is_blocked_without_success_report(self):
        (self.directory / "evaluation.json").unlink()
        code, errors = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED", errors)
        self.assertFalse((self.directory / "summary.json").exists())

    def test_main_refuses_to_overwrite_existing_summary(self):
        output = self.directory / "summary.json"
        output.write_text("previous evidence", encoding="utf-8")
        code, errors = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("already exists", errors)
        self.assertEqual(output.read_text(), "previous evidence")

    def test_main_malformed_xml_is_blocked(self):
        (self.directory / "tests.xml").write_text("<invalid", encoding="utf-8")
        code, errors = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED", errors)
        self.assertFalse((self.directory / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()
