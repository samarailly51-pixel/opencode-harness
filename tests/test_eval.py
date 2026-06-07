from pathlib import Path
import json
import tempfile
import unittest

from opencode_harness.config import AgentConfig, HarnessConfig, ModelConfig, PermissionConfig
from opencode_harness.eval import EvalCaseResult, EvalReport, load_eval_suite, run_eval_suite


class EvalTests(unittest.TestCase):
    def test_load_eval_suite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            suite = Path(temp_dir) / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "smoke",
                        "cases": [{"id": "one", "task": "inspect", "expect_contains": "done"}],
                    }
                ),
                encoding="utf-8",
            )

            name, cases = load_eval_suite(suite)

            self.assertEqual(name, "smoke")
            self.assertEqual(cases[0].id, "one")
            self.assertEqual(cases[0].expect_contains, "done")

    def test_run_eval_suite_with_mock(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "repo").mkdir()
            (root / "repo" / "README.md").write_text("# Demo\n", encoding="utf-8")
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "smoke",
                        "cases": [
                            {
                                "id": "inspect",
                                "task": "inspect this repo",
                                "workspace": "repo",
                                "expect_contains": "Mock run completed",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            config = HarnessConfig(
                model=ModelConfig(provider="mock"),
                agent=AgentConfig(max_steps=2, context_chars=1000),
                permissions=PermissionConfig(),
            )

            report = run_eval_suite(suite, config, root / "eval-runs")

            self.assertEqual(report.total, 1)
            self.assertEqual(report.passed, 1)
            self.assertTrue(Path(report.results[0].trace).exists())
            self.assertTrue(Path(report.results[0].session).exists())
            report_md = next((root / "eval-runs").glob("*/report.md"))
            markdown = report_md.read_text(encoding="utf-8")
            self.assertIn("# Eval Report: smoke", markdown)
            self.assertIn("| inspect | PASS |", markdown)
            self.assertIn("Mock run completed", markdown)

    def test_eval_report_markdown_escapes_table_cells(self) -> None:
        report = EvalReport(
            suite="demo",
            started_at="20260607-000000",
            model_provider="mock",
            model_name="mock-coder",
            total=1,
            passed=0,
            results=[
                EvalCaseResult(
                    id="case|one",
                    ok=False,
                    finished=True,
                    steps=1,
                    seconds=0.1234,
                    summary="failed",
                    trace="eval-runs/demo/trace.jsonl",
                    session="eval-runs/demo/session.json",
                    error=None,
                )
            ],
        )

        markdown = report.to_markdown()

        self.assertIn("case\\|one", markdown)
        self.assertIn("0/1", markdown)
