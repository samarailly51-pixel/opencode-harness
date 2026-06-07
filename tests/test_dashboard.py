from pathlib import Path
import tempfile
import unittest

from opencode_harness.dashboard import discover_eval_reports, render_eval_dashboard, write_eval_dashboard
from opencode_harness.eval import EvalCaseResult, EvalReport


class DashboardTests(unittest.TestCase):
    def test_discover_eval_reports_and_render_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = root / "eval-runs" / "run-one"
            run_dir.mkdir(parents=True)
            report = EvalReport(
                suite="demo <suite>",
                started_at="20260607-000000",
                model_provider="mock",
                model_name="mock-coder",
                total=2,
                passed=1,
                results=[
                    EvalCaseResult("pass", True, True, 1, 0.1, "ok", "pass.jsonl", "pass.session.json"),
                    EvalCaseResult(
                        "fail",
                        False,
                        False,
                        2,
                        0.2,
                        "bad",
                        "fail.jsonl",
                        "fail.session.json",
                        failure_type="max_steps",
                    ),
                ],
            )
            (run_dir / "report.json").write_text(report.to_json(), encoding="utf-8")
            (run_dir / "report.html").write_text("<html></html>", encoding="utf-8")

            items = discover_eval_reports([root / "eval-runs"])
            html = render_eval_dashboard(items, output_path=root / "eval-runs" / "dashboard.html")

            self.assertEqual(len(items), 1)
            self.assertIn("OpenCode Harness Eval Dashboard", html)
            self.assertIn("demo &lt;suite&gt;", html)
            self.assertIn("max_steps=1", html)
            self.assertIn("run-one/report.html", html)
            self.assertNotIn("demo <suite>", html)

    def test_write_eval_dashboard_creates_file_for_empty_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "dashboard" / "index.html"

            write_eval_dashboard([], output)

            self.assertTrue(output.exists())
            self.assertIn("No eval reports found", output.read_text(encoding="utf-8"))
