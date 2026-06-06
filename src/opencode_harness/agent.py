from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .messages import Message, SYSTEM_PROMPT
from .models import ChatModel, ToolCall
from .repo_map import build_repo_map, pack_context
from .session import SessionState
from .tools import ToolRegistry, ToolResult
from .trace import TraceWriter


@dataclass(frozen=True)
class AgentResult:
    summary: str
    steps: int
    finished: bool


class Agent:
    def __init__(
        self,
        model: ChatModel,
        tools: ToolRegistry,
        trace: TraceWriter,
        max_steps: int,
        workspace: Path | None = None,
        context_chars: int = 6000,
        session: SessionState | None = None,
        session_path: Path | None = None,
    ) -> None:
        self.model = model
        self.tools = tools
        self.trace = trace
        self.max_steps = max_steps
        self.workspace = workspace
        self.context_chars = context_chars
        self.session = session
        self.session_path = session_path

    def run(self, task: str) -> AgentResult:
        messages = self._initial_messages(task)
        self.trace.write("task.start", {"task": task, "max_steps": self.max_steps})
        self._save_session(task, messages, 0, "running")

        for step in range(1, self.max_steps + 1):
            response = self.model.complete(messages, tools=True, extra_tools=self.tools.tool_specs())
            self.trace.write(
                "model.response",
                {
                    "step": step,
                    "content": response.content,
                    "tool_calls": response.tool_calls,
                },
            )
            tool_call = self._next_tool_call(response.tool_calls, response.content)

            if tool_call is None:
                summary = response.content.strip()
                self.trace.write("task.finish", {"step": step, "summary": summary, "mode": "text"})
                self._save_session(task, messages + [Message("assistant", response.content)], step, "finished")
                self.trace.update_latest()
                return AgentResult(summary=summary, steps=step, finished=True)

            result = self.tools.run(tool_call.name, tool_call.args)
            self.trace.write(
                "tool.result",
                {
                    "step": step,
                    "tool": tool_call.name,
                    "args": tool_call.args,
                    "ok": result.ok,
                    "content": result.content,
                },
            )

            if tool_call.name == "finish":
                self.trace.write("task.finish", {"step": step, "summary": result.content, "mode": "tool"})
                self._save_session(task, messages + [Message("assistant", response.content)], step, "finished")
                self.trace.update_latest()
                return AgentResult(summary=result.content, steps=step, finished=True)

            messages.append(Message("assistant", _assistant_tool_message(response.content, tool_call)))
            messages.append(Message("user", _format_observation(tool_call.name, result)))
            self._save_session(task, messages, step, "running")

        summary = f"Stopped after reaching max_steps={self.max_steps}."
        self.trace.write("task.stop", {"summary": summary})
        self._save_session(task, messages, self.max_steps, "stopped")
        self.trace.update_latest()
        return AgentResult(summary=summary, steps=self.max_steps, finished=False)

    def _parse_tool_call(self, content: str) -> tuple[str | None, dict[str, object]]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return None, {}
        if not isinstance(data, dict) or "tool" not in data:
            return None, {}
        args = data.get("args", {})
        if not isinstance(args, dict):
            args = {}
        return str(data["tool"]), args

    def _next_tool_call(self, tool_calls: list[ToolCall] | None, content: str) -> ToolCall | None:
        if tool_calls:
            return tool_calls[0]
        tool_name, tool_args = self._parse_tool_call(content)
        if tool_name is None:
            return None
        return ToolCall(name=tool_name, args=tool_args)

    def _initial_messages(self, task: str) -> list[Message]:
        if self.session and self.session.messages:
            messages = self.session.messages[:]
            messages.append(Message("user", f"Continue task: {task}"))
            return messages
        return [
            Message("system", SYSTEM_PROMPT),
            *self._repo_context_messages(task),
            Message("user", task),
        ]

    def _repo_context_messages(self, task: str) -> list[Message]:
        if self.workspace is None or self.context_chars <= 0:
            return []
        repo_map = build_repo_map(self.workspace)
        context = pack_context(repo_map, task, max_chars=self.context_chars)
        self.trace.write("context.pack", {"chars": len(context), "files": len(repo_map.files)})
        return [Message("user", "Initial repository context:\n" + context)]

    def _save_session(
        self,
        task: str,
        messages: list[Message],
        steps: int,
        status: str,
    ) -> None:
        if self.session is None or self.session_path is None:
            return
        self.session.task = task
        self.session.messages = messages
        self.session.steps = steps
        self.session.status = status
        self.session.save(self.session_path)


def _format_observation(tool_name: str, result: ToolResult) -> str:
    status = "ok" if result.ok else "error"
    return f"Observation from {tool_name} ({status}):\n{result.content}"


def _assistant_tool_message(content: str, tool_call: ToolCall) -> str:
    if content.strip():
        return content
    return json.dumps(
        {"tool": tool_call.name, "args": tool_call.args},
        ensure_ascii=False,
    )
