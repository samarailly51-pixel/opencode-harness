import io
import json
import tempfile
import tomllib
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from opencode_harness import __version__
from opencode_harness.cli import main


class CliTests(unittest.TestCase):
    def test_version_command_prints_package_version(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            status = main(["version"])

        self.assertEqual(status, 0)
        self.assertIn(f"opencode-harness {__version__}", output.getvalue())

    def test_package_version_matches_pyproject(self) -> None:
        data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(data["project"]["version"], __version__)

    def test_diagnose_command_prints_failure_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            report_path.write_text(
                json.dumps(
                    {
                        "suite": "demo",
                        "started_at": "20260619-000000",
                        "model_provider": "mock",
                        "model_name": "mock-coder",
                        "total": 1,
                        "passed": 0,
                        "results": [
                            {
                                "id": "inspect",
                                "ok": False,
                                "finished": False,
                                "steps": 1,
                                "seconds": 0.1,
                                "summary": "Stopped after reaching max_steps=1.",
                                "trace": "trace.jsonl",
                                "session": "session.json",
                                "failure_type": "max_steps",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                status = main(["diagnose", str(report_path)])

            self.assertEqual(status, 0)
            self.assertIn("# Failure-Mode Diagnosis", output.getvalue())
            self.assertIn("Tool-loop overrun", output.getvalue())
