from pathlib import Path
import json
import tempfile
import unittest

from opencode_harness.diagnosis import compare_diagnosis_reports, diagnose_eval_reports
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

    def test_diagnose_eval_reports_uses_trace_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "case.jsonl"
            events = [
                {"time": "t0", "type": "task.start", "data": {"finish_marker": "DONE_MARKER"}},
                {"time": "t1", "type": "model.response", "data": {"step": 1, "content": ""}},
                {
                    "time": "t2",
                    "type": "tool.result",
                    "data": {"step": 1, "tool": "read_file", "ok": True, "content": "one"},
                },
                {"time": "t3", "type": "model.response", "data": {"step": 2, "content": ""}},
                {
                    "time": "t4",
                    "type": "tool.result",
                    "data": {"step": 2, "tool": "read_file", "ok": True, "content": "two"},
                },
                {"time": "t5", "type": "model.response", "data": {"step": 3, "content": ""}},
                {
                    "time": "t6",
                    "type": "tool.result",
                    "data": {"step": 3, "tool": "read_file", "ok": True, "content": "three"},
                },
                {"time": "t7", "type": "task.finish", "data": {"step": 4, "summary": "done"}},
            ]
            trace_path.write_text(
                "\n".join(json.dumps(event) for event in events),
                encoding="utf-8",
            )
            report = EvalReport(
                suite="trace-aware",
                started_at="20260620-000000",
                model_provider="mock",
                model_name="mock-coder",
                total=1,
                passed=0,
                results=[
                    EvalCaseResult(
                        id="case",
                        ok=False,
                        finished=True,
                        steps=4,
                        seconds=1.0,
                        summary="done",
                        trace=str(trace_path),
                        session="case.session.json",
                        failure_type="expectation_mismatch",
                    )
                ],
            )

            markdown = diagnose_eval_reports([report])

            self.assertIn("Trace Signals", markdown)
            self.assertIn("last_tools=read_file > read_file > read_file", markdown)
            self.assertIn("repeated_tail=read_file", markdown)
            self.assertIn("marker=missing", markdown)
            self.assertIn("omitted the required finish marker", markdown)

    def test_compare_diagnosis_reports_shows_before_after_delta(self) -> None:
        before = EvalReport(
            suite="suite",
            started_at="before",
            model_provider="mock",
            model_name="mock-coder",
            total=2,
            passed=1,
            results=[
                EvalCaseResult("case-a", True, True, 2, 1.0, "ok", "missing.jsonl", "a.session.json"),
                EvalCaseResult(
                    "case-b",
                    False,
                    False,
                    5,
                    2.0,
                    "Stopped after reaching max_steps=5.",
                    "missing.jsonl",
                    "b.session.json",
                    failure_type="max_steps",
                ),
            ],
        )
        after = EvalReport(
            suite="suite",
            started_at="after",
            model_provider="mock",
            model_name="mock-coder",
            total=2,
            passed=2,
            results=[
                EvalCaseResult("case-a", True, True, 2, 1.0, "ok", "missing.jsonl", "a.session.json"),
                EvalCaseResult("case-b", True, True, 3, 1.5, "fixed", "missing.jsonl", "b.session.json"),
            ],
        )

        markdown = compare_diagnosis_reports([before], [after], "Guard off", "Guard on")

        self.assertIn("# Before/After Diagnosis Comparison", markdown)
        self.assertIn("Guard off", markdown)
        self.assertIn("Guard on", markdown)
        self.assertIn("Pass Rate", markdown)
        self.assertIn("`max_steps`", markdown)
        self.assertIn("fixed", markdown)
