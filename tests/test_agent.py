from pathlib import Path
import json
import unittest

from opencode_harness.agent import Agent
from opencode_harness.config import PermissionConfig
from opencode_harness.messages import Message
from opencode_harness.models import ChatModel, MockModel, ModelResponse, ToolCall
from opencode_harness.tools import ToolRegistry
from opencode_harness.trace import TraceWriter


class NativeToolModel(ChatModel):
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages: list[Message], tools: bool = False, extra_tools=None) -> ModelResponse:
        self.calls += 1
        assert tools
        if self.calls == 1:
            return ModelResponse("", tool_calls=[ToolCall("list_files", {"path": "."})])
        return ModelResponse("", tool_calls=[ToolCall("finish", {"summary": "native tool completed"})])


class MarkerAwareModel(ChatModel):
    def __init__(self) -> None:
        self.calls = 0
        self.second_call_messages: list[Message] = []

    def complete(self, messages: list[Message], tools: bool = False, extra_tools=None) -> ModelResponse:
        self.calls += 1
        if self.calls == 1:
            return ModelResponse("", tool_calls=[ToolCall("list_files", {"path": "."})])
        self.second_call_messages = messages[:]
        return ModelResponse("", tool_calls=[ToolCall("finish", {"summary": "DONE_MARKER completed"})])


class AgentTests(unittest.TestCase):
    def test_mock_agent_writes_trace(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            trace = TraceWriter(workspace / "runs" / "test.jsonl")
            agent = Agent(
                model=MockModel(),
                tools=ToolRegistry(workspace, PermissionConfig()),
                trace=trace,
                max_steps=2,
            )

            result = agent.run("inspect this repo")

            self.assertEqual(result.steps, 2)
            self.assertTrue(result.finished)
            self.assertIn("Mock run completed", result.summary)
            self.assertTrue(trace.path.exists())
            self.assertTrue((workspace / "runs" / "latest.jsonl").exists())
            model_events = [
                json.loads(line)
                for line in trace.path.read_text(encoding="utf-8").splitlines()
                if '"type": "model.response"' in line
            ]
            self.assertEqual(model_events[0]["data"]["transcript"]["provider"], "mock")
            self.assertEqual(
                model_events[0]["data"]["transcript"]["request_format"],
                "opencode-harness.mock.v1",
            )

    def test_agent_consumes_native_tool_call(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "README.md").write_text("# Demo\n", encoding="utf-8")
            trace = TraceWriter(workspace / "runs" / "native.jsonl")
            agent = Agent(
                model=NativeToolModel(),
                tools=ToolRegistry(workspace, PermissionConfig()),
                trace=trace,
                max_steps=2,
            )

            result = agent.run("inspect")

            self.assertTrue(result.finished)
            self.assertEqual(result.summary, "native tool completed")

    def test_agent_adds_finish_marker_and_final_step_guard(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "README.md").write_text("# Demo\n", encoding="utf-8")
            trace = TraceWriter(workspace / "runs" / "marker.jsonl")
            model = MarkerAwareModel()
            agent = Agent(
                model=model,
                tools=ToolRegistry(workspace, PermissionConfig()),
                trace=trace,
                max_steps=2,
                finish_marker="DONE_MARKER",
            )

            result = agent.run("inspect")

            self.assertTrue(result.finished)
            self.assertEqual(result.summary, "DONE_MARKER completed")
            second_call_text = "\n".join(message.content for message in model.second_call_messages)
            self.assertIn("final summary must include exact marker `DONE_MARKER`", second_call_text)
            self.assertIn("Final-step guard", second_call_text)
