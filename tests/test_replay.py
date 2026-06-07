from pathlib import Path
import tempfile
import unittest

from opencode_harness.replay import load_trace, render_timeline, summarize_trace


TRACE_TEXT = """
{"time":"t0","type":"task.start","data":{"task":"inspect","max_steps":2}}
{"time":"t1","type":"model.response","data":{"step":1,"content":"{\\"tool\\":\\"list_files\\",\\"args\\":{}}"}}
{"time":"t2","type":"tool.result","data":{"step":1,"tool":"list_files","args":{},"ok":true,"content":"README.md"}}
{"time":"t3","type":"task.finish","data":{"step":1,"summary":"done","mode":"tool"}}
""".strip()

TRACE_WITH_TRANSCRIPT = """
{"time":"t0","type":"task.start","data":{"task":"inspect","max_steps":2}}
{"time":"t1","type":"model.response","data":{"step":1,"content":"done","transcript":{"provider":"mock","request_format":"opencode-harness.mock.v1","response_format":"opencode-harness.mock.v1","request":{"messages":[]},"response":{"content":"done"}}}}
{"time":"t2","type":"task.finish","data":{"step":1,"summary":"done","mode":"text"}}
""".strip()


class ReplayTests(unittest.TestCase):
    def test_summarize_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.jsonl"
            path.write_text(TRACE_TEXT, encoding="utf-8")

            events = load_trace(path)
            summary = summarize_trace(events)

            self.assertEqual(summary.events, 4)
            self.assertEqual(summary.model_calls, 1)
            self.assertEqual(summary.transcripts, 0)
            self.assertEqual(summary.tool_calls, 1)
            self.assertTrue(summary.finished)
            self.assertEqual(summary.final_summary, "done")

    def test_render_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.jsonl"
            path.write_text(TRACE_TEXT, encoding="utf-8")

            timeline = render_timeline(load_trace(path))

            self.assertIn("[task] inspect", timeline)
            self.assertIn("tool list_files -> ok", timeline)

    def test_replay_summarizes_provider_transcripts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.jsonl"
            path.write_text(TRACE_WITH_TRANSCRIPT, encoding="utf-8")

            events = load_trace(path)
            summary = summarize_trace(events)
            timeline = render_timeline(events)

            self.assertEqual(summary.transcripts, 1)
            self.assertIn("transcript: mock opencode-harness.mock.v1", timeline)

    def test_invalid_trace_reports_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.jsonl"
            path.write_text("{bad json}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid JSON"):
                load_trace(path)
