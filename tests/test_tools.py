from pathlib import Path
import tempfile
import unittest

from opencode_harness.config import PermissionConfig
from opencode_harness.mcp import ExternalToolSpec
from opencode_harness.tools import ToolRegistry
from opencode_harness.tools_types import ToolResult


class ToolTests(unittest.TestCase):
    def test_read_file_inside_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "hello.txt").write_text("hello", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig())

            result = tools.run("read_file", {"path": "hello.txt"})

            self.assertTrue(result.ok)
            self.assertEqual(result.content, "hello")


    def test_blocks_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            tools = ToolRegistry(workspace, PermissionConfig())

            with self.assertRaisesRegex(ValueError, "escapes workspace"):
                tools.run("read_file", {"path": "../outside.txt"})

    def test_write_file_requires_permission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            tools = ToolRegistry(workspace, PermissionConfig(allow_write=False))

            result = tools.run("write_file", {"path": "note.txt", "content": "hello"})

            self.assertFalse(result.ok)
            self.assertFalse((workspace / "note.txt").exists())

    def test_replace_text_with_permission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "note.txt"
            file_path.write_text("hello world", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig(allow_write=True))

            result = tools.run(
                "replace_text",
                {"path": "note.txt", "old": "world", "new": "harness"},
            )

            self.assertTrue(result.ok)
            self.assertEqual(file_path.read_text(encoding="utf-8"), "hello harness")

    def test_apply_patch_with_permission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "note.txt"
            file_path.write_text("hello world\n", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig(allow_write=True))

            result = tools.run(
                "apply_patch",
                {
                    "patch": (
                        "--- a/note.txt\n"
                        "+++ b/note.txt\n"
                        "@@\n"
                        "-hello world\n"
                        "+hello harness\n"
                    )
                },
            )

            self.assertTrue(result.ok)
            self.assertEqual(file_path.read_text(encoding="utf-8"), "hello harness\n")

    def test_apply_patch_with_line_numbered_hunk(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "note.txt"
            file_path.write_text("one\ntwo\nthree\n", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig(allow_write=True))

            result = tools.run(
                "apply_patch",
                {
                    "patch": (
                        "--- a/note.txt\n"
                        "+++ b/note.txt\n"
                        "@@ -2,1 +2,1 @@\n"
                        "-two\n"
                        "+TWO\n"
                    )
                },
            )

            self.assertTrue(result.ok)
            self.assertEqual(file_path.read_text(encoding="utf-8"), "one\nTWO\nthree\n")

    def test_apply_patch_with_two_hunks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "note.txt"
            file_path.write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig(allow_write=True))

            result = tools.run(
                "apply_patch",
                {
                    "patch": (
                        "--- a/note.txt\n"
                        "+++ b/note.txt\n"
                        "@@ -1,1 +1,1 @@\n"
                        "-one\n"
                        "+ONE\n"
                        "@@ -4,1 +4,1 @@\n"
                        "-four\n"
                        "+FOUR\n"
                    )
                },
            )

            self.assertTrue(result.ok)
            self.assertEqual(file_path.read_text(encoding="utf-8"), "ONE\ntwo\nthree\nFOUR\n")

    def test_apply_patch_uses_nearby_line_when_header_drifts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "note.txt"
            file_path.write_text("zero\none\ntwo\nthree\n", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig(allow_write=True))

            result = tools.run(
                "apply_patch",
                {
                    "patch": (
                        "--- a/note.txt\n"
                        "+++ b/note.txt\n"
                        "@@ -2,1 +2,1 @@\n"
                        "-two\n"
                        "+TWO\n"
                    )
                },
            )

            self.assertTrue(result.ok)
            self.assertEqual(file_path.read_text(encoding="utf-8"), "zero\none\nTWO\nthree\n")

    def test_apply_patch_reports_missing_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "note.txt"
            file_path.write_text("one\ntwo\n", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig(allow_write=True))

            result = tools.run(
                "apply_patch",
                {
                    "patch": (
                        "--- a/note.txt\n"
                        "+++ b/note.txt\n"
                        "@@ -1,1 +1,1 @@\n"
                        "-missing\n"
                        "+found\n"
                    )
                },
            )

            self.assertFalse(result.ok)
            self.assertIn("Patch context not found", result.content)

    def test_todo_set_updates_session(self) -> None:
        from opencode_harness.session import SessionState

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session = SessionState()
            tools = ToolRegistry(workspace, PermissionConfig(), session=session)

            result = tools.run(
                "todo_set",
                {"items": [{"title": "inspect", "status": "in_progress"}]},
            )

            self.assertTrue(result.ok)
            self.assertEqual(session.todos[0].title, "inspect")
            self.assertIn("in_progress", result.content)

    def test_repo_map_tool(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "app.py").write_text("def main():\n    pass\n", encoding="utf-8")
            tools = ToolRegistry(workspace, PermissionConfig())

            result = tools.run("repo_map", {})

            self.assertTrue(result.ok)
            self.assertIn("app.py", result.content)
            self.assertIn("main", result.content)

    def test_external_tool_without_handler_reports_missing_client(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            tools = ToolRegistry(
                workspace,
                PermissionConfig(),
                external_tools=[
                    ExternalToolSpec(
                        name="mcp_lookup",
                        description="Lookup.",
                        input_schema={"type": "object", "properties": {}},
                        server="docs",
                    )
                ],
            )

            result = tools.run("mcp_lookup", {})

            self.assertFalse(result.ok)
            self.assertIn("no client is attached", result.content)

    def test_external_tool_handler_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            tools = ToolRegistry(
                workspace,
                PermissionConfig(),
                external_tools=[
                    ExternalToolSpec(
                        name="mcp_lookup",
                        description="Lookup.",
                        input_schema={"type": "object", "properties": {}},
                    )
                ],
                external_handlers={
                    "mcp_lookup": lambda args: ToolResult(True, f"found {args['q']}"),
                },
            )

            result = tools.run("mcp_lookup", {"q": "agent"})

            self.assertTrue(result.ok)
            self.assertEqual(result.content, "found agent")
