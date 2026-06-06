from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class TraceEvent:
    time: str
    type: str
    data: dict[str, Any]


@dataclass(frozen=True)
class ReplaySummary:
    events: int
    model_calls: int
    tool_calls: int
    failed_tools: int
    steps: int
    finished: bool
    final_summary: str


def load_trace(path: Path) -> list[TraceEvent]:
    events: list[TraceEvent] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON at {path}:{line_no}") from error
        events.append(
            TraceEvent(
                time=str(data.get("time", "")),
                type=str(data.get("type", "")),
                data=data.get("data", {}),
            )
        )
    return events


def summarize_trace(events: list[TraceEvent]) -> ReplaySummary:
    model_calls = sum(1 for event in events if event.type == "model.response")
    tool_events = [event for event in events if event.type == "tool.result"]
    failed_tools = sum(1 for event in tool_events if not event.data.get("ok", False))
    finish_events = [event for event in events if event.type == "task.finish"]
    stop_events = [event for event in events if event.type == "task.stop"]
    final_event = finish_events[-1] if finish_events else stop_events[-1] if stop_events else None
    final_summary = str(final_event.data.get("summary", "")) if final_event else ""
    steps = 0
    for event in events:
        step = event.data.get("step")
        if isinstance(step, int):
            steps = max(steps, step)
    return ReplaySummary(
        events=len(events),
        model_calls=model_calls,
        tool_calls=len(tool_events),
        failed_tools=failed_tools,
        steps=steps,
        finished=bool(finish_events),
        final_summary=final_summary,
    )


def render_timeline(events: list[TraceEvent], show_content: bool = False) -> str:
    lines: list[str] = []
    for event in events:
        if event.type == "context.pack":
            lines.append(
                f"[context] packed {event.data.get('chars', '?')} chars from {event.data.get('files', '?')} files"
            )
        elif event.type == "task.start":
            lines.append(f"[task] {event.data.get('task', '')}")
        elif event.type == "model.response":
            content = str(event.data.get("content", ""))
            lines.append(f"[step {event.data.get('step')}] model response: {_preview(content)}")
            if show_content:
                lines.append(_indent(content))
        elif event.type == "tool.result":
            status = "ok" if event.data.get("ok") else "error"
            tool = event.data.get("tool")
            lines.append(f"[step {event.data.get('step')}] tool {tool} -> {status}")
            if show_content:
                lines.append(_indent(str(event.data.get("content", ""))))
        elif event.type == "task.finish":
            lines.append(f"[finish] {event.data.get('summary', '')}")
        elif event.type == "task.stop":
            lines.append(f"[stop] {event.data.get('summary', '')}")
        else:
            lines.append(f"[{event.type}] {event.data}")
    return "\n".join(lines)


def render_summary(summary: ReplaySummary) -> str:
    return "\n".join(
        [
            f"Events: {summary.events}",
            f"Steps: {summary.steps}",
            f"Model calls: {summary.model_calls}",
            f"Tool calls: {summary.tool_calls}",
            f"Failed tools: {summary.failed_tools}",
            f"Finished: {summary.finished}",
            f"Final summary: {summary.final_summary}",
        ]
    )


def _preview(text: str, limit: int = 120) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit - 3] + "..."


def _indent(text: str) -> str:
    return "\n".join("  " + line for line in text.splitlines())
