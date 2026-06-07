from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import json
import time

from .agent import Agent
from .config import HarnessConfig
from .models import build_model
from .mcp import ExternalToolSpec
from .mcp_client import McpServerSpec, StdioMcpClient
from .session import SessionState
from .tools import ToolRegistry
from .trace import TraceWriter


@dataclass(frozen=True)
class EvalCase:
    id: str
    task: str
    workspace: str = "."
    expect_contains: str | None = None


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
            "| Case | Status | Finished | Steps | Seconds | Trace | Session |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
        for result in self.results:
            status = "PASS" if result.ok else "FAIL"
            lines.append(
                "| "
                + " | ".join(
                    [
                        _md_escape(result.id),
                        status,
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
                    _md_block(result.summary or "(no summary)"),
                    "",
                ]
            )
            if result.error:
                lines.extend(["Error:", "", _md_block(result.error), ""])
        return "\n".join(lines).rstrip() + "\n"


def load_eval_suite(path: Path) -> tuple[str, list[EvalCase]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    suite_name = str(data.get("name", path.stem))
    cases = [
        EvalCase(
            id=str(item["id"]),
            task=str(item["task"]),
            workspace=str(item.get("workspace", ".")),
            expect_contains=item.get("expect_contains"),
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
            )
            for item in data.get("results", [])
        ],
    )


def compare_eval_reports(reports: list[EvalReport]) -> str:
    lines = [
        "# Eval Report Comparison",
        "",
        "| Suite | Provider | Model | Passed | Pass Rate | Avg Steps | Total Seconds |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
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
) -> EvalReport:
    suite_name, cases = load_eval_suite(suite_path)
    started_at = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = output_dir / f"{suite_path.stem}-{started_at}"
    run_dir.mkdir(parents=True, exist_ok=True)
    model = build_model(config.model)
    external_tools, external_handlers, mcp_clients = _mcp_runtime_from_config(config)
    results: list[EvalCaseResult] = []

    try:
        for case in cases:
            start = time.perf_counter()
            workspace = (suite_path.parent / case.workspace).resolve()
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
                )
            else:
                ok = agent_result.finished
                if case.expect_contains:
                    ok = ok and case.expect_contains in agent_result.summary
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


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _md_link_path(path: str) -> str:
    return Path(path).as_posix().replace(" ", "%20")


def _md_block(text: str) -> str:
    return "```text\n" + text.replace("```", "'''") + "\n```"


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
    return f"{status} ({result.steps} steps, {result.seconds:.2f}s)"
