from pathlib import Path
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
