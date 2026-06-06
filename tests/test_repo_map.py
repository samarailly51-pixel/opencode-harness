from pathlib import Path
import tempfile
import unittest

from opencode_harness.repo_map import build_repo_map, extract_symbols, pack_context


class RepoMapTests(unittest.TestCase):
    def test_extract_python_symbols(self) -> None:
        symbols = extract_symbols(
            "class Agent:\n    pass\n\ndef run_task():\n    pass\n",
            "python",
        )

        self.assertEqual(symbols, ["Agent", "run_task"])

    def test_build_repo_map_ignores_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "src").mkdir()
            (workspace / "src" / "app.py").write_text("def main():\n    pass\n", encoding="utf-8")
            (workspace / "runs").mkdir()
            (workspace / "runs" / "trace.jsonl").write_text("{}", encoding="utf-8")

            repo_map = build_repo_map(workspace)

            paths = [file.path for file in repo_map.files]
            self.assertEqual(paths, ["src/app.py"])
            self.assertEqual(repo_map.files[0].symbols, ["main"])

    def test_pack_context_prioritizes_query_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "auth_service.py").write_text("class AuthService:\n    pass\n", encoding="utf-8")
            (workspace / "billing.py").write_text("class Billing:\n    pass\n", encoding="utf-8")
            repo_map = build_repo_map(workspace)

            context = pack_context(repo_map, "auth failure")

            self.assertIn("auth_service.py", context)
            self.assertIn("AuthService", context)
