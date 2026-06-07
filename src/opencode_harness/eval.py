from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from html import escape
from pathlib import Path
import json
import shutil
import subprocess
import sys
import time
from uuid import uuid4

from .agent import Agent
from .config import HarnessConfig
from .models import build_model
from .mcp import ExternalToolSpec
from .mcp_client import McpServerSpec, StdioMcpClient
from .permissions import check_shell_permission
from .replay import load_trace, summarize_trace
from .session import SessionState
from .tools import ToolRegistry
from .trace import TraceWriter


@dataclass(frozen=True)
class EvalCase:
    id: str
    task: str
    workspace: str = "."
    expect_contains: str | None = None
    workspace_template: str | None = None
    verify_command: str | None = None


@dataclass(frozen=True)
class EvalCaseResult:
    id: str
    ok: bool
    finished: bool
    steps: int
    seconds: float
    summary: str
    trace: str
    session: str
    error: str | None = None
    failure_type: str | None = None


@dataclass(frozen=True)
class EvalReport:
    suite: str
    started_at: str
    model_provider: str
    model_name: str
    total: int
    passed: int
    results: list[EvalCaseResult]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def to_markdown(self) -> str:
        rate = 0 if self.total == 0 else (self.passed / self.total) * 100
        lines = [
            f"# Eval Report: {self.suite}",
            "",
            f"- Started: `{self.started_at}`",
            f"- Model provider: `{self.model_provider}`",
            f"- Model name: `{self.model_name}`",
            f"- Passed: `{self.passed}/{self.total}` ({rate:.1f}%)",
            "",
            "## Results",
            "",
            "| Case | Status | Failure | Finished | Steps | Seconds | Trace | Session |",
            "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
        ]
        for result in self.results:
            status = "PASS" if result.ok else "FAIL"
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md_escape(result.id),
                        status,
                        _failure_label(result),
                        str(result.finished),
                        str(result.steps),
                        f"{result.seconds:.3f}",
                        f"[trace]({_md_link_path(result.trace)})",
                        f"[session]({_md_link_path(result.session)})",
                    ]
                )
                + " |"
            )
        lines.extend(["", "## Case Summaries", ""])
        for result in self.results:
            status = "PASS" if result.ok else "FAIL"
            lines.extend(
                [
                    f"### {status}: `{result.id}`",
                    "",
                ]
            )
            if result.failure_type:
                lines.extend([f"- Failure type: `{result.failure_type}`", ""])
            lines.extend([_md_block(result.summary or "(no summary)"), ""])
            if result.error:
                lines.extend(["Error:", "", _md_block(result.error), ""])
        return "\n".join(lines).rstrip() + "\n"

    def to_html(self) -> str:
        rate = 0 if self.total == 0 else (self.passed / self.total) * 100
        rows = []
        for result in self.results:
            status = "PASS" if result.ok else "FAIL"
            status_class = "pass" if result.ok else "fail"
            rows.append(
                "<tr>"
                f"<td>{escape(result.id)}</td>"
                f"<td><span class=\"badge {status_class}\">{status}</span></td>"
                f"<td>{escape(_failure_label(result))}</td>"
                f"<td>{escape(str(result.finished))}</td>"
                f"<td class=\"num\">{result.steps}</td>"
                f"<td class=\"num\">{result.seconds:.3f}</td>"
                f"<td><a href=\"{escape(_md_link_path(result.trace))}\">trace</a></td>"
                f"<td><a href=\"{escape(_md_link_path(result.session))}\">session</a></td>"
                "</tr>"
            )
        summaries = []
        for result in self.results:
            status = "PASS" if result.ok else "FAIL"
            status_class = "pass" if result.ok else "fail"
            error = ""
            if result.error:
                error = f"<h4>Error</h4><pre>{escape(result.error)}</pre>"
            failure = ""
            if result.failure_type:
                failure = f"<p><strong>Failure type:</strong> <code>{escape(result.failure_type)}</code></p>"
            summaries.append(
                "<section class=\"case-summary\">"
                f"<h3><span class=\"badge {status_class}\">{status}</span> {escape(result.id)}</h3>"
                f"{failure}"
                f"<pre>{escape(result.summary or '(no summary)')}</pre>"
                f"{error}"
                "</section>"
            )
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eval Report: {escape(self.suite)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #202124; }}
    main {{ max-width: 1120px; margin: 0 auto; }}
    h1, h2, h3 {{ line-height: 1.2; }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 20px 0; }}
    .metric {{ border: 1px solid #dadce0; border-radius: 8px; padding: 12px; background: #fafafa; }}
    .metric strong {{ display: block; font-size: 0.8rem; color: #5f6368; text-transform: uppercase; }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0 28px; }}
    th, td {{ border-bottom: 1px solid #e8eaed; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f8fafd; font-weight: 600; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 0.8rem; font-weight: 700; }}
    .pass {{ background: #e6f4ea; color: #137333; }}
    .fail {{ background: #fce8e6; color: #a50e0e; }}
    pre {{ white-space: pre-wrap; background: #f8fafd; border: 1px solid #e8eaed; border-radius: 8px; padding: 12px; overflow-x: auto; }}
    a {{ color: #0b57d0; }}
  </style>
</head>
<body>
<main>
  <h1>Eval Report: {escape(self.suite)}</h1>
  <section class="meta">
    <div class="metric"><strong>Started</strong>{escape(self.started_at)}</div>
    <div class="metric"><strong>Provider</strong>{escape(self.model_provider)}</div>
    <div class="metric"><strong>Model</strong>{escape(self.model_name)}</div>
    <div class="metric"><strong>Passed</strong>{self.passed}/{self.total} ({rate:.1f}%)</div>
  </section>
  <h2>Results</h2>
  <table>
    <thead>
      <tr><th>Case</th><th>Status</th><th>Failure</th><th>Finished</th><th>Steps</th><th>Seconds</th><th>Trace</th><th>Session</th></tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
  <h2>Case Summaries</h2>
  {"".join(summaries)}
</main>
</body>
</html>
"""


def load_eval_suite(path: Path) -> tuple[str, list[EvalCase]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    suite_name = str(data.get("name", path.stem))
    cases = [
        EvalCase(
            id=str(item["id"]),
            task=str(item["task"]),
            workspace=str(item.get("workspace", ".")),
            expect_contains=item.get("expect_contains"),
            workspace_template=item.get("workspace_template"),
            verify_command=item.get("verify_command"),
        )
        for item in data.get("cases", [])
    ]
    return suite_name, cases


def load_eval_report(path: Path) -> EvalReport:
    report_path = path / "report.json" if path.is_dir() else path
    data = json.loads(report_path.read_text(encoding="utf-8"))
    return EvalReport(
        suite=str(data["suite"]),
        started_at=str(data["started_at"]),
        model_provider=str(data["model_provider"]),
        model_name=str(data["model_name"]),
        total=int(data["total"]),
        passed=int(data["passed"]),
        results=[
            EvalCaseResult(
                id=str(item["id"]),
                ok=bool(item["ok"]),
                finished=bool(item["finished"]),
                steps=int(item["steps"]),
                seconds=float(item["seconds"]),
                summary=str(item.get("summary", "")),
                trace=str(item["trace"]),
                session=str(item["session"]),
                error=item.get("error"),
                failure_type=item.get("failure_type"),
            )
            for item in data.get("results", [])
        ],
    )


def compare_eval_reports(reports: list[EvalReport]) -> str:
    lines = [
        "# Eval Report Comparison",
        "",
        "| Suite | Provider | Model | Passed | Pass Rate | Failures | Avg Steps | Total Seconds |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for report in reports:
        pass_rate = 0 if report.total == 0 else (report.passed / report.total) * 100
        avg_steps = _average(result.steps for result in report.results)
        total_seconds = sum(result.seconds for result in report.results)
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(report.suite),
                    _md_escape(report.model_provider),
                    _md_escape(report.model_name),
                    f"{report.passed}/{report.total}",
                    f"{pass_rate:.1f}%",
                    _failure_breakdown(report.results),
                    f"{avg_steps:.2f}",
                    f"{total_seconds:.3f}",
                ]
            )
            + " |"
        )

    case_ids = sorted({result.id for report in reports for result in report.results})
    if case_ids:
        lines.extend(["", "## Case Matrix", ""])
        header = ["Case", *[_md_escape(_report_label(report)) for report in reports]]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---", *["---" for _ in reports]]) + " |")
        for case_id in case_ids:
            row = [_md_escape(case_id)]
            for report in reports:
                result = next((item for item in report.results if item.id == case_id), None)
                row.append(_case_cell(result))
            lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines).rstrip() + "\n"


def run_eval_suite(
    suite_path: Path,
    config: HarnessConfig,
    output_dir: Path,
    run_label: str | None = None,
) -> EvalReport:
    suite_name, cases = load_eval_suite(suite_path)
    now = datetime.now()
    started_at = now.strftime("%Y%m%d-%H%M%S")
    run_id = f"{now.strftime('%Y%m%d-%H%M%S-%f')}-{uuid4().hex[:8]}"
    label = f"-{_slug(run_label)}" if run_label else ""
    run_dir = output_dir / f"{suite_path.stem}{label}-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    model = build_model(config.model)
    external_tools, external_handlers, mcp_clients = _mcp_runtime_from_config(config)
    results: list[EvalCaseResult] = []

    try:
        for case in cases:
            start = time.perf_counter()
            workspace = _case_workspace(suite_path, run_dir, case)
            trace_path = run_dir / f"{case.id}.jsonl"
            session_path = run_dir / f"{case.id}.session.json"
            trace = TraceWriter(trace_path)
            session = SessionState(task=case.task)
            tools = ToolRegistry(
                workspace,
                config.permissions,
                session=session,
                external_tools=external_tools,
                external_handlers=external_handlers,
            )
            agent = Agent(
                model=model,
                tools=tools,
                trace=trace,
                max_steps=config.agent.max_steps,
                workspace=workspace,
                context_chars=config.agent.context_chars,
                session=session,
                session_path=session_path,
            )
            try:
                agent_result = agent.run(case.task)
                error = None
            except Exception as exc:  # pragma: no cover - defensive report path
                agent_result = None
                error = str(exc)
            seconds = time.perf_counter() - start

            if agent_result is None:
                failure_type = _classify_failure(None, error, case.expect_contains, trace_path)
                result = EvalCaseResult(
                    id=case.id,
                    ok=False,
                    finished=False,
                    steps=0,
                    seconds=seconds,
                    summary="",
                    trace=str(trace_path),
                    session=str(session_path),
                    error=error,
                    failure_type=failure_type,
                )
            else:
                ok = agent_result.finished
                if case.expect_contains:
                    ok = ok and case.expect_contains in agent_result.summary
                verify_error = None
                if ok and case.verify_command:
                    verify_error = _run_verify_command(case.verify_command, workspace, config)
                    ok = verify_error is None
                    if verify_error:
                        error = verify_error
                failure_type = _classify_failure(agent_result, error, case.expect_contains, trace_path)
                result = EvalCaseResult(
                    id=case.id,
                    ok=ok,
                    finished=agent_result.finished,
                    steps=agent_result.steps,
                    seconds=seconds,
                    summary=agent_result.summary,
                    trace=str(trace_path),
                    session=str(session_path),
                    error=error,
                    failure_type=failure_type if not ok else None,
                )
            results.append(result)
    finally:
        for client in mcp_clients:
            client.close()

    report = EvalReport(
        suite=suite_name,
        started_at=started_at,
        model_provider=config.model.provider,
        model_name=config.model.model,
        total=len(results),
        passed=sum(1 for result in results if result.ok),
        results=results,
    )
    (run_dir / "report.json").write_text(report.to_json(), encoding="utf-8")
    (run_dir / "report.md").write_text(report.to_markdown(), encoding="utf-8")
    (run_dir / "report.html").write_text(report.to_html(), encoding="utf-8")
    return report


def _mcp_runtime_from_config(
    config: HarnessConfig,
) -> tuple[list[ExternalToolSpec], dict[str, object], list[StdioMcpClient]]:
    tools = [
        ExternalToolSpec(
            name=tool.name,
            description=tool.description or f"External MCP tool {tool.name}.",
            input_schema=tool.input_schema or {"type": "object", "properties": {}},
            server=tool.server,
        )
        for tool in config.mcp_tools
    ]
    clients: dict[str, StdioMcpClient] = {}
    handlers = {}
    for server in config.mcp_servers:
        client = StdioMcpClient(
            McpServerSpec(name=server.name, command=server.command, args=server.args)
        )
        clients[server.name] = client
        for tool in client.list_tools():
            tools.append(tool)
            handlers[tool.name] = client.call_tool
    for tool in tools:
        if tool.server and tool.server in clients and tool.name not in handlers:
            handlers[tool.name] = clients[tool.server].call_tool
    return tools, handlers, list(clients.values())


def _case_workspace(suite_path: Path, run_dir: Path, case: EvalCase) -> Path:
    if case.workspace_template is None:
        return (suite_path.parent / case.workspace).resolve()
    source = (suite_path.parent / case.workspace_template).resolve()
    target = run_dir / "workspaces" / _slug(case.id)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return target.resolve()


def _run_verify_command(command: str, workspace: Path, config: HarnessConfig) -> str | None:
    decision = check_shell_permission(command, config.permissions)
    if not decision.allowed:
        return f"verify_command blocked by policy: {decision.reason}"
    completed = subprocess.run(
        _runtime_command(command),
        cwd=workspace,
        shell=True,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if completed.returncode == 0:
        return None
    output = completed.stdout
    if completed.stderr:
        output += "\n[stderr]\n" + completed.stderr
    detail = output.strip() or f"exit code {completed.returncode}"
    return f"verify_command failed: {detail}"


def _runtime_command(command: str) -> str:
    if command.startswith("python -m "):
        return f'"{sys.executable}" {command[len("python "):]}'
    return command


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _md_link_path(path: str) -> str:
    return Path(path).as_posix().replace(" ", "%20")


def _md_block(text: str) -> str:
    return "```text\n" + text.replace("```", "'''") + "\n```"


def _slug(text: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in text).strip("-") or "run"


def _average(values: object) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)


def _report_label(report: EvalReport) -> str:
    return f"{report.model_provider}/{report.model_name}"


def _case_cell(result: EvalCaseResult | None) -> str:
    if result is None:
        return "-"
    status = "PASS" if result.ok else "FAIL"
    failure = f":{result.failure_type}" if result.failure_type else ""
    return f"{status}{failure} ({result.steps} steps, {result.seconds:.2f}s)"


def _failure_label(result: EvalCaseResult) -> str:
    return "-" if result.ok or not result.failure_type else _md_escape(result.failure_type)


def _failure_breakdown(results: list[EvalCaseResult]) -> str:
    counts: dict[str, int] = {}
    for result in results:
        if result.ok:
            continue
        failure_type = result.failure_type or "unknown"
        counts[failure_type] = counts.get(failure_type, 0) + 1
    if not counts:
        return "-"
    return ", ".join(f"{_md_escape(name)}={count}" for name, count in sorted(counts.items()))


def _classify_failure(
    agent_result: object,
    error: str | None,
    expect_contains: str | None,
    trace_path: Path,
) -> str | None:
    if error:
        if error.startswith("verify_command"):
            return "verification_failure"
        return "exception"
    trace_summary = None
    if trace_path.exists():
        trace_summary = summarize_trace(load_trace(trace_path))
    failed_tools = trace_summary.failed_tools if trace_summary is not None else 0
    finished = bool(getattr(agent_result, "finished", False)) if agent_result is not None else False
    summary = str(getattr(agent_result, "summary", "")) if agent_result is not None else ""
    if failed_tools and not finished:
        return "tool_failure"
    if not finished:
        return "max_steps"
    if expect_contains and expect_contains not in summary:
        return "expectation_mismatch"
    if failed_tools:
        return "recovered_tool_failure"
    return None
