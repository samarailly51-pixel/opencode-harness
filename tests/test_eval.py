from pathlib import Path
from datetime import datetime
import json
import tempfile
import unittest
from unittest.mock import patch

from opencode_harness.config import AgentConfig, HarnessConfig, ModelConfig, PermissionConfig
from opencode_harness.eval import (
    EvalCaseResult,
    EvalReport,
    compare_eval_reports,
    load_eval_report,
    load_eval_suite,
    run_eval_suite,
)
from opencode_harness.messages import Message
from opencode_harness.models import ChatModel, ModelResponse, ToolCall


class VerificationRepairModel(ChatModel):
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages: list[Message], tools: bool = False, extra_tools=None) -> ModelResponse:
        self.calls += 1
        text = "\n".join(message.content for message in messages)
        if "Repair verification failed" in text and self.calls == 2:
            return ModelResponse(
                "",
                tool_calls=[
                    ToolCall(
                        "replace_text",
                        {"path": "broken.py", "old": "return 1", "new": "return 2"},
                    )
                ],
            )
        return ModelResponse("", tool_calls=[ToolCall("finish", {"summary": "REPAIR_DONE"})])


class EvalTests(unittest.TestCase):
    def test_load_eval_suite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            suite = Path(temp_dir) / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "smoke",
                        "cases": [
                            {
                                "id": "one",
                                "task": "inspect",
                                "expect_contains": "done",
                                "workspace_template": "fixture",
                                "verify_command": "python -m unittest",
                                "verify_feedback_attempts": 2,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            name, cases = load_eval_suite(suite)

            self.assertEqual(name, "smoke")
            self.assertEqual(cases[0].id, "one")
            self.assertEqual(cases[0].expect_contains, "done")
            self.assertEqual(cases[0].workspace_template, "fixture")
            self.assertEqual(cases[0].verify_command, "python -m unittest")
            self.assertEqual(cases[0].verify_feedback_attempts, 2)

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
            self.assertIsNone(report.results[0].failure_type)
            self.assertTrue(Path(report.results[0].trace).exists())
            self.assertTrue(Path(report.results[0].session).exists())
            report_md = next((root / "eval-runs").glob("*/report.md"))
            markdown = report_md.read_text(encoding="utf-8")
            self.assertIn("# Eval Report: smoke", markdown)
            self.assertIn("| inspect | PASS |", markdown)
            self.assertIn("Mock run completed", markdown)
            report_html = next((root / "eval-runs").glob("*/report.html"))
            html = report_html.read_text(encoding="utf-8")
            self.assertIn("<title>Eval Report: smoke</title>", html)
            self.assertIn("Mock run completed", html)
            trace_path = Path(report.results[0].trace)
            events = [
                json.loads(line)
                for line in trace_path.read_text(encoding="utf-8").splitlines()
            ]
            task_start = next(event for event in events if event["type"] == "task.start")
            self.assertEqual(task_start["data"]["finish_marker"], "Mock run completed")

    def test_run_eval_suite_uses_unique_dirs_within_same_second(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "repo").mkdir()
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

            class FakeDatetime:
                calls = [
                    datetime(2026, 6, 7, 1, 2, 3, 100),
                    datetime(2026, 6, 7, 1, 2, 3, 100),
                ]

                @classmethod
                def now(cls) -> datetime:
                    return cls.calls.pop(0)

            with patch("opencode_harness.eval.datetime", FakeDatetime):
                first = run_eval_suite(suite, config, root / "eval-runs")
                second = run_eval_suite(suite, config, root / "eval-runs")

            self.assertEqual(first.started_at, "20260607-010203")
            self.assertEqual(second.started_at, "20260607-010203")
            run_dirs = sorted((root / "eval-runs").iterdir())
            self.assertEqual(len(run_dirs), 2)
            self.assertNotEqual(run_dirs[0].name, run_dirs[1].name)

    def test_run_eval_suite_classifies_expectation_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "repo").mkdir()
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "mismatch",
                        "cases": [
                            {
                                "id": "inspect",
                                "task": "inspect this repo",
                                "workspace": "repo",
                                "expect_contains": "text that is not in the mock summary",
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

            self.assertEqual(report.passed, 0)
            self.assertEqual(report.results[0].failure_type, "expectation_mismatch")
            report_md = next((root / "eval-runs").glob("*/report.md"))
            markdown = report_md.read_text(encoding="utf-8")
            self.assertIn("Failure type: `expectation_mismatch`", markdown)

    def test_run_eval_suite_classifies_max_steps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "repo").mkdir()
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "stopped",
                        "cases": [{"id": "inspect", "task": "inspect this repo", "workspace": "repo"}],
                    }
                ),
                encoding="utf-8",
            )
            config = HarnessConfig(
                model=ModelConfig(provider="mock"),
                agent=AgentConfig(max_steps=1, context_chars=1000),
                permissions=PermissionConfig(),
            )

            report = run_eval_suite(suite, config, root / "eval-runs")

            self.assertEqual(report.passed, 0)
            self.assertEqual(report.results[0].failure_type, "max_steps")

    def test_run_eval_suite_copies_workspace_template_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "fixture"
            (template / "tests").mkdir(parents=True)
            (template / "tests" / "__init__.py").write_text("", encoding="utf-8")
            (template / "mathy.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
            (template / "tests" / "test_mathy.py").write_text(
                "import unittest\nfrom mathy import add\n\n"
                "class MathyTests(unittest.TestCase):\n"
                "    def test_add(self):\n"
                "        self.assertEqual(add(2, 3), 5)\n",
                encoding="utf-8",
            )
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "repair",
                        "cases": [
                            {
                                "id": "already-fixed",
                                "task": "finish",
                                "workspace_template": "fixture",
                                "expect_contains": "Mock run completed",
                                "verify_command": "python -m unittest discover -s tests -t .",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            config = HarnessConfig(
                model=ModelConfig(provider="mock"),
                agent=AgentConfig(max_steps=1, context_chars=0),
                permissions=PermissionConfig(),
            )

            report = run_eval_suite(suite, config, root / "eval-runs")

            self.assertEqual(report.passed, 1)
            copied = next((root / "eval-runs").glob("*/workspaces/already-fixed/mathy.py"))
            self.assertTrue(copied.exists())

    def test_run_eval_suite_classifies_verification_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "fixture"
            (template / "tests").mkdir(parents=True)
            (template / "tests" / "__init__.py").write_text("", encoding="utf-8")
            (template / "broken.py").write_text("def value():\n    return 1\n", encoding="utf-8")
            (template / "tests" / "test_broken.py").write_text(
                "import unittest\nfrom broken import value\n\n"
                "class BrokenTests(unittest.TestCase):\n"
                "    def test_value(self):\n"
                "        self.assertEqual(value(), 2)\n",
                encoding="utf-8",
            )
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "repair",
                        "cases": [
                            {
                                "id": "still-broken",
                                "task": "finish",
                                "workspace_template": "fixture",
                                "expect_contains": "Mock run completed",
                                "verify_command": "python -m unittest discover -s tests -t .",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            config = HarnessConfig(
                model=ModelConfig(provider="mock"),
                agent=AgentConfig(max_steps=1, context_chars=0),
                permissions=PermissionConfig(),
            )

            report = run_eval_suite(suite, config, root / "eval-runs")

            self.assertEqual(report.passed, 0)
            self.assertEqual(report.results[0].failure_type, "verification_failure")

    def test_run_eval_suite_feeds_verification_failure_back_to_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "fixture"
            (template / "tests").mkdir(parents=True)
            (template / "tests" / "__init__.py").write_text("", encoding="utf-8")
            (template / "broken.py").write_text("def value():\n    return 1\n", encoding="utf-8")
            (template / "tests" / "test_broken.py").write_text(
                "import unittest\nfrom broken import value\n\n"
                "class BrokenTests(unittest.TestCase):\n"
                "    def test_value(self):\n"
                "        self.assertEqual(value(), 2)\n",
                encoding="utf-8",
            )
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "name": "repair-feedback",
                        "cases": [
                            {
                                "id": "fix-after-feedback",
                                "task": "fix broken.py and finish with REPAIR_DONE",
                                "workspace_template": "fixture",
                                "expect_contains": "REPAIR_DONE",
                                "verify_command": "python -m unittest discover -s tests -t .",
                                "verify_feedback_attempts": 1,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            config = HarnessConfig(
                model=ModelConfig(provider="mock"),
                agent=AgentConfig(max_steps=2, context_chars=0),
                permissions=PermissionConfig(allow_write=True),
            )

            with patch("opencode_harness.eval.build_model", return_value=VerificationRepairModel()):
                report = run_eval_suite(suite, config, root / "eval-runs")

            self.assertEqual(report.passed, 1)
            self.assertEqual(report.results[0].steps, 3)
            trace_events = [
                json.loads(line)
                for line in Path(report.results[0].trace).read_text(encoding="utf-8").splitlines()
            ]
            self.assertTrue(any(event["type"] == "verify.feedback" for event in trace_events))
            session_text = Path(report.results[0].session).read_text(encoding="utf-8")
            self.assertIn("Repair verification failed", session_text)
            copied = next((root / "eval-runs").glob("*/workspaces/fix-after-feedback/broken.py"))
            self.assertIn("return 2", copied.read_text(encoding="utf-8"))

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
                    failure_type="expectation_mismatch",
                )
            ],
        )

        markdown = report.to_markdown()

        self.assertIn("case\\|one", markdown)
        self.assertIn("0/1", markdown)
        self.assertIn("expectation_mismatch", markdown)

    def test_eval_report_html_escapes_content(self) -> None:
        report = EvalReport(
            suite="<demo>",
            started_at="20260607-000000",
            model_provider="mock",
            model_name="mock-coder",
            total=1,
            passed=0,
            results=[
                EvalCaseResult(
                    id="<case>",
                    ok=False,
                    finished=True,
                    steps=1,
                    seconds=0.1234,
                    summary="<script>alert(1)</script>",
                    trace="trace.jsonl",
                    session="session.json",
                    error="<bad>",
                    failure_type="exception",
                )
            ],
        )

        html = report.to_html()

        self.assertIn("&lt;demo&gt;", html)
        self.assertIn("<code>exception</code>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_load_eval_report_from_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            run_dir.mkdir()
            report = EvalReport(
                suite="demo",
                started_at="20260607-000000",
                model_provider="mock",
                model_name="mock-coder",
                total=1,
                passed=1,
                results=[
                    EvalCaseResult(
                        id="one",
                        ok=True,
                        finished=True,
                        steps=2,
                        seconds=0.5,
                        summary="ok",
                        trace="trace.jsonl",
                        session="session.json",
                    )
                ],
            )
            (run_dir / "report.json").write_text(report.to_json(), encoding="utf-8")

            loaded = load_eval_report(run_dir)

            self.assertEqual(loaded.suite, "demo")
            self.assertEqual(loaded.results[0].id, "one")
            self.assertIsNone(loaded.results[0].failure_type)

    def test_load_eval_report_reads_failure_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            run_dir.mkdir()
            (run_dir / "report.json").write_text(
                json.dumps(
                    {
                        "suite": "demo",
                        "started_at": "20260607-000000",
                        "model_provider": "mock",
                        "model_name": "mock-coder",
                        "total": 1,
                        "passed": 0,
                        "results": [
                            {
                                "id": "one",
                                "ok": False,
                                "finished": False,
                                "steps": 1,
                                "seconds": 0.5,
                                "summary": "stopped",
                                "trace": "trace.jsonl",
                                "session": "session.json",
                                "failure_type": "max_steps",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            loaded = load_eval_report(run_dir)

            self.assertEqual(loaded.results[0].failure_type, "max_steps")

    def test_compare_eval_reports(self) -> None:
        reports = [
            EvalReport(
                suite="suite",
                started_at="t1",
                model_provider="deepseek",
                model_name="deepseek-chat",
                total=1,
                passed=1,
                results=[
                    EvalCaseResult("case-a", True, True, 2, 1.0, "ok", "a.jsonl", "a.json")
                ],
            ),
            EvalReport(
                suite="suite",
                started_at="t2",
                model_provider="qwen",
                model_name="qwen-plus",
                total=1,
                passed=0,
                results=[
                    EvalCaseResult(
                        "case-a",
                        False,
                        True,
                        3,
                        2.0,
                        "bad",
                        "b.jsonl",
                        "b.json",
                        failure_type="expectation_mismatch",
                    )
                ],
            ),
        ]

        markdown = compare_eval_reports(reports)

        self.assertIn("# Eval Report Comparison", markdown)
        self.assertIn("deepseek-chat", markdown)
        self.assertIn("qwen-plus", markdown)
        self.assertIn("Failures", markdown)
        self.assertIn("expectation_mismatch=1", markdown)
        self.assertIn("PASS (2 steps", markdown)
        self.assertIn("FAIL:expectation_mismatch (3 steps", markdown)
