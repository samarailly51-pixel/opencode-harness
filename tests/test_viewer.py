from pathlib import Path
import tempfile
import unittest

from opencode_harness.replay import load_trace
from opencode_harness.viewer import render_trace_html, render_tui, write_trace_html


TRACE_TEXT = """
{"time":"t0","type":"task.start","data":{"task":"inspect <repo>","max_steps":2}}
{"time":"t1","type":"model.response","data":{"step":1,"content":"done","transcript":{"provider":"mock"}}}
{"time":"t2","type":"tool.result","data":{"step":1,"tool":"list_files","ok":false,"content":"<bad>"}}
{"time":"t3","type":"task.stop","data":{"step":1,"summary":"stopped"}}
""".strip()


class ViewerTests(unittest.TestCase):
    def test_render_tui_trace_summary_and_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.jsonl"
            path.write_text(TRACE_TEXT, encoding="utf-8")

            output = render_tui(load_trace(path), width=72)

            self.assertIn("OpenCode Harness Trace", output)
            self.assertIn("Failed tools: 1", output)
            self.assertIn("model.response transcript", output)
            self.assertIn("tool.result list_files -> error", output)

    def test_render_trace_html_escapes_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.jsonl"
            path.write_text(TRACE_TEXT, encoding="utf-8")

            html = render_trace_html(load_trace(path), title="Trace <Demo>")

            self.assertIn("Trace &lt;Demo&gt;", html)
            self.assertIn("inspect &lt;repo&gt;", html)
            self.assertIn("&lt;bad&gt;", html)
            self.assertNotIn("inspect <repo>", html)

    def test_write_trace_html_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = root / "trace.jsonl"
            output = root / "viewer" / "trace.html"
            path.write_text(TRACE_TEXT, encoding="utf-8")

            write_trace_html(path, output, load_trace(path))

            self.assertTrue(output.exists())
            self.assertIn("Trace Viewer: trace.jsonl", output.read_text(encoding="utf-8"))
