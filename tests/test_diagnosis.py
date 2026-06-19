import unittest

from opencode_harness.diagnosis import diagnose_eval_reports
from opencode_harness.eval import EvalCaseResult, EvalReport


class DiagnosisTests(unittest.TestCase):
    def test_diagnose_eval_reports_groups_failure_modes(self) -> None:
        report = EvalReport(
            suite="deepseek-long-context",
            started_at="20260619-000000",
            model_provider="openai-compatible",
            model_name="deepseek-chat",
            total=2,
            passed=0,
            results=[
                EvalCaseResult(
                    id="repo-wide-summary",
                    ok=False,
                    finished=False,
                    steps=8,
                    seconds=12.0,
                    summary="Stopped after reaching max_steps=8.",
                    trace="eval-runs/repo-wide-summary.jsonl",
                    session="eval-runs/repo-wide-summary.session.json",
                    failure_type="max_steps",
                ),
                EvalCaseResult(
                    id="repair-calculator",
                    ok=False,
                    finished=True,
                    steps=5,
                    seconds=9.0,
                    summary="Fixed calculator but missed marker.",
                    trace="eval-runs/repair-calculator.jsonl",
                    session="eval-runs/repair-calculator.session.json",
                    failure_type="expectation_mismatch",
                ),
            ],
        )

        markdown = diagnose_eval_reports([report])

        self.assertIn("# Failure-Mode Diagnosis", markdown)
        self.assertIn("`max_steps`", markdown)
        self.assertIn("`expectation_mismatch`", markdown)
        self.assertIn("Tool-loop overrun", markdown)
        self.assertIn("Repair finalization gap", markdown)
        self.assertIn("Recommended Fixes", markdown)
