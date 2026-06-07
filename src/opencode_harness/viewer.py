from __future__ import annotations

from html import escape
from pathlib import Path
import json
import textwrap

from .replay import TraceEvent, render_summary, summarize_trace


def render_tui(events: list[TraceEvent], width: int = 100, show_content: bool = False) -> str:
    width = max(60, width)
    summary = summarize_trace(events)
    lines: list[str] = []
    lines.extend(
        _box(
            "OpenCode Harness Trace",
            [
                f"Events: {summary.events}",
                f"Steps: {summary.steps}",
                f"Finished: {summary.finished}",
                f"Model calls: {summary.model_calls}",
                f"Tool calls: {summary.tool_calls}",
                f"Failed tools: {summary.failed_tools}",
                f"Transcripts: {summary.transcripts}",
                f"Final summary: {summary.final_summary or '(none)'}",
            ],
            width,
        )
    )
    lines.append("")
    timeline = _timeline_lines(events, show_content=show_content)
    lines.extend(_box("Timeline", timeline or ["(empty trace)"], width))
    return "\n".join(lines)


def render_trace_html(events: list[TraceEvent], title: str = "Trace Viewer") -> str:
    summary = summarize_trace(events)
    event_cards = []
    for index, event in enumerate(events, start=1):
        step = event.data.get("step", "")
        label = f"step {step}" if step != "" else event.type
        data = json.dumps(event.data, ensure_ascii=False, indent=2)
        event_cards.append(
            "<section class=\"event\">"
            f"<div class=\"event-head\"><span class=\"type\">{escape(event.type)}</span>"
            f"<span>{escape(label)}</span><span>{escape(event.time)}</span></div>"
            f"<pre>{escape(data)}</pre>"
            "</section>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #202124; background: #f6f8fb; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
    h1 {{ margin: 0 0 18px; font-size: 1.8rem; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 20px; }}
    .metric {{ background: #fff; border: 1px solid #dfe3ea; border-radius: 8px; padding: 12px; }}
    .metric strong {{ display: block; color: #5f6368; font-size: 0.78rem; text-transform: uppercase; margin-bottom: 4px; }}
    .event {{ background: #fff; border: 1px solid #dfe3ea; border-radius: 8px; margin: 12px 0; overflow: hidden; }}
    .event-head {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between; background: #eef3f8; padding: 10px 12px; color: #3c4043; }}
    .type {{ font-weight: 700; color: #174ea6; }}
    pre {{ margin: 0; padding: 12px; white-space: pre-wrap; overflow-x: auto; }}
  </style>
</head>
<body>
<main>
  <h1>{escape(title)}</h1>
  <section class="metrics">
    <div class="metric"><strong>Events</strong>{summary.events}</div>
    <div class="metric"><strong>Steps</strong>{summary.steps}</div>
    <div class="metric"><strong>Finished</strong>{escape(str(summary.finished))}</div>
    <div class="metric"><strong>Model Calls</strong>{summary.model_calls}</div>
    <div class="metric"><strong>Tool Calls</strong>{summary.tool_calls}</div>
    <div class="metric"><strong>Failed Tools</strong>{summary.failed_tools}</div>
    <div class="metric"><strong>Transcripts</strong>{summary.transcripts}</div>
  </section>
  <section class="event">
    <div class="event-head"><span class="type">summary</span></div>
    <pre>{escape(render_summary(summary))}</pre>
  </section>
  {"".join(event_cards)}
</main>
</body>
</html>
"""


def write_trace_html(trace_path: Path, output_path: Path, events: list[TraceEvent]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_trace_html(events, title=f"Trace Viewer: {trace_path.name}"),
        encoding="utf-8",
    )


def _timeline_lines(events: list[TraceEvent], show_content: bool) -> list[str]:
    lines: list[str] = []
    for index, event in enumerate(events, start=1):
        step = event.data.get("step")
        prefix = f"{index:03d}"
        if isinstance(step, int):
            prefix += f" step {step}"
        if event.type == "task.start":
            lines.append(f"{prefix} task.start {event.data.get('task', '')}")
        elif event.type == "context.pack":
            lines.append(
                f"{prefix} context.pack {event.data.get('chars', '?')} chars / {event.data.get('files', '?')} files"
            )
        elif event.type == "model.response":
            transcript = " transcript" if event.data.get("transcript") else ""
            lines.append(f"{prefix} model.response{transcript} {_preview(str(event.data.get('content', '')))}")
        elif event.type == "tool.result":
            status = "ok" if event.data.get("ok") else "error"
            lines.append(f"{prefix} tool.result {event.data.get('tool')} -> {status}")
        elif event.type == "task.finish":
            lines.append(f"{prefix} task.finish {event.data.get('summary', '')}")
        elif event.type == "task.stop":
            lines.append(f"{prefix} task.stop {event.data.get('summary', '')}")
        else:
            lines.append(f"{prefix} {event.type}")
        if show_content and event.data:
            lines.extend("  " + line for line in json.dumps(event.data, ensure_ascii=False, indent=2).splitlines())
    return lines


def _box(title: str, body: list[str], width: int) -> list[str]:
    inner = width - 4
    lines = ["+" + "-" * (width - 2) + "+"]
    lines.append("| " + title[:inner].ljust(inner) + " |")
    lines.append("| " + "-" * inner + " |")
    for item in body:
        wrapped = textwrap.wrap(item, width=inner) or [""]
        for line in wrapped:
            lines.append("| " + line.ljust(inner) + " |")
    lines.append("+" + "-" * (width - 2) + "+")
    return lines


def _preview(text: str, limit: int = 140) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."
