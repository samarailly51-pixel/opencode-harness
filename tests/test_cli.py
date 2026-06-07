import io
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
