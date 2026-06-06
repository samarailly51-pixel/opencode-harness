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
