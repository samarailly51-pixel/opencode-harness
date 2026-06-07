from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

from .agent import Agent
from .config import HarnessConfig, ModelConfig, PermissionConfig, load_config
from .eval import compare_eval_reports, load_eval_report, run_eval_suite
from .labs import run_provider_comparison
from .mcp_runtime import build_mcp_runtime
from .models import MockModel, build_model
from .providers import PRESETS, apply_preset
from .replay import load_trace, render_summary, render_timeline, summarize_trace
from .session import SessionState
from .tools import ToolRegistry
from .trace import TraceWriter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="och", description="OpenCode Harness CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a one-shot coding-agent task")
    run_parser.add_argument("task")
    _add_common_model_args(run_parser)

    chat_parser = subparsers.add_parser("chat", help="Run an interactive chat loop")
    _add_common_model_args(chat_parser)
    chat_parser.add_argument("--mock", action="store_true", help="Use the offline mock model")

    init_parser = subparsers.add_parser("init", help="Create och.config.toml from the example")
    init_parser.add_argument("--force", action="store_true", help="Overwrite an existing config")

    trace_parser = subparsers.add_parser("trace", help="Print a JSONL trace file")
    trace_parser.add_argument("path")

    replay_parser = subparsers.add_parser("replay", help="Replay a trace as a readable timeline")
    replay_parser.add_argument("path", type=Path)
    replay_parser.add_argument("--summary", action="store_true", help="Print only summary statistics")
    replay_parser.add_argument("--show-content", action="store_true", help="Show full model/tool content")

    eval_parser = subparsers.add_parser("eval", help="Run an eval suite")
    eval_parser.add_argument("suite", type=Path)
    eval_parser.add_argument("--output-dir", type=Path, default=Path("eval-runs"))
    _add_common_model_args(eval_parser)

    compare_parser = subparsers.add_parser("compare", help="Compare eval report.json files")
    compare_parser.add_argument("reports", nargs="+", type=Path, help="report.json files or eval run directories")
    compare_parser.add_argument("--output", type=Path, help="Write Markdown comparison to this path")

    lab_compare_parser = subparsers.add_parser("lab-compare", help="Run one eval suite across provider presets")
    lab_compare_parser.add_argument("suite", type=Path)
    lab_compare_parser.add_argument("--presets", nargs="+", choices=sorted(PRESETS), default=["deepseek", "qwen", "openai", "claude"])
    lab_compare_parser.add_argument("--output-dir", type=Path, default=Path("eval-runs"))
    lab_compare_parser.add_argument("--comparison-output", type=Path, required=True)
    lab_compare_parser.add_argument("--include-missing-keys", action="store_true", help="Run providers even when their API key env var is missing")
    lab_compare_parser.add_argument("--config", type=Path, help="Path to och config TOML")
    lab_compare_parser.add_argument("--max-steps", type=int, help="Agent max steps")
    lab_compare_parser.add_argument("--context-chars", type=int, help="Max repository context characters")
    lab_compare_parser.add_argument("--allow-write", action="store_true", help="Allow file-writing tools")
    lab_compare_parser.add_argument("--approval-mode", choices=["never", "ask"], help="Approval mode for risky tool calls")

    args = parser.parse_args(argv)
    if args.command == "init":
        return _init_config(args.force)
    if args.command == "trace":
        return _print_trace(Path(args.path))
    if args.command == "replay":
        return _replay_trace(args.path, args.summary, args.show_content)
    if args.command == "run":
        config = _config_from_args(args)
        return _run_task(args.task, config, args.workspace, args.session, args.resume)
    if args.command == "chat":
        config = _config_from_args(args, force_mock=args.mock)
        return _chat(config)
    if args.command == "eval":
        config = _config_from_args(args)
        return _run_eval(args.suite, config, args.output_dir)
    if args.command == "compare":
        return _compare_reports(args.reports, args.output)
    if args.command == "lab-compare":
        config = _lab_config_from_args(args)
        return _run_lab_compare(
            args.suite,
            args.presets,
            config,
            args.output_dir,
            args.comparison_output,
            skip_missing_keys=not args.include_missing_keys,
        )
    return 1


def _add_common_model_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, help="Path to och config TOML")
    parser.add_argument("--preset", choices=sorted(PRESETS), help="Provider preset")
    parser.add_argument("--provider", choices=["mock", "openai-compatible", "anthropic"], help="Model provider")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--api-key-env", help="Environment variable containing API key")
    parser.add_argument("--max-steps", type=int, help="Agent max steps")
    parser.add_argument("--context-chars", type=int, help="Max repository context characters")
    parser.add_argument("--allow-write", action="store_true", help="Allow file-writing tools")
    parser.add_argument("--approval-mode", choices=["never", "ask"], help="Approval mode for risky tool calls")
    parser.add_argument("--session", type=Path, help="Session JSON path")
    parser.add_argument("--resume", action="store_true", help="Resume from --session if it exists")
    parser.add_argument("--workspace", type=Path, default=Path("."), help="Workspace path")


def _config_from_args(args: argparse.Namespace, force_mock: bool = False) -> HarnessConfig:
    config = load_config(args.config)
    model = config.model
    if force_mock:
        model = ModelConfig(provider="mock")
    else:
        if args.preset:
            model = apply_preset(args.preset, model)
        model = ModelConfig(
            provider=args.provider or model.provider,
            model=args.model or model.model,
            base_url=args.base_url or model.base_url,
            api_key_env=args.api_key_env or model.api_key_env,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
        )

    agent = config.agent
    if args.max_steps is not None:
        agent = type(agent)(max_steps=args.max_steps, context_chars=agent.context_chars)
    if args.context_chars is not None:
        agent = type(agent)(max_steps=agent.max_steps, context_chars=args.context_chars)
    permissions = config.permissions
    if args.allow_write:
        permissions = PermissionConfig(
            allow_write=True,
            allow_shell=permissions.allow_shell,
            allow_network=permissions.allow_network,
            approval_mode=permissions.approval_mode,
        )
    if args.approval_mode is not None:
        permissions = PermissionConfig(
            allow_write=permissions.allow_write,
            allow_shell=permissions.allow_shell,
            allow_network=permissions.allow_network,
            approval_mode=args.approval_mode,
        )
    return HarnessConfig(
        model=model,
        agent=agent,
        permissions=permissions,
        mcp_tools=config.mcp_tools,
        mcp_servers=config.mcp_servers,
    )


def _lab_config_from_args(args: argparse.Namespace) -> HarnessConfig:
    config = load_config(args.config)
    agent = config.agent
    if args.max_steps is not None:
        agent = type(agent)(max_steps=args.max_steps, context_chars=agent.context_chars)
    if args.context_chars is not None:
        agent = type(agent)(max_steps=agent.max_steps, context_chars=args.context_chars)
    permissions = config.permissions
    if args.allow_write:
        permissions = PermissionConfig(
            allow_write=True,
            allow_shell=permissions.allow_shell,
            allow_network=permissions.allow_network,
            approval_mode=permissions.approval_mode,
        )
    if args.approval_mode is not None:
        permissions = PermissionConfig(
            allow_write=permissions.allow_write,
            allow_shell=permissions.allow_shell,
            allow_network=permissions.allow_network,
            approval_mode=args.approval_mode,
        )
    return HarnessConfig(
        model=config.model,
        agent=agent,
        permissions=permissions,
        mcp_tools=config.mcp_tools,
        mcp_servers=config.mcp_servers,
    )


def _run_task(
    task: str,
    config: HarnessConfig,
    workspace: Path | None = None,
    session_path: Path | None = None,
    resume: bool = False,
) -> int:
    workspace = (workspace or Path(".")).resolve()
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    trace = TraceWriter(workspace / "runs" / f"{run_id}.jsonl")
    session_path = session_path or workspace / "runs" / f"{run_id}.session.json"
    session = SessionState.load(session_path) if resume and session_path.exists() else SessionState(task=task)
    model = build_model(config.model)
    mcp_runtime = build_mcp_runtime(config)
    tools = ToolRegistry(
        workspace,
        config.permissions,
        session=session,
        external_tools=mcp_runtime.tools,
        external_handlers=mcp_runtime.handlers,
        external_approval_modes=mcp_runtime.approval_modes,
        approval_callback=None,
    )
    try:
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
        result = agent.run(task)
        print(result.summary)
        print(f"\nTrace: {trace.path}")
        print(f"Session: {session_path}")
        return 0 if result.finished else 2
    finally:
        mcp_runtime.close()


def _chat(config: HarnessConfig) -> int:
    model = build_model(config.model) if config.model.provider != "mock" else MockModel()
    print("OpenCode Harness chat. Type /exit to quit.")
    while True:
        try:
            task = input("och> ").strip()
        except EOFError:
            print()
            return 0
        if task in {"/exit", "/quit"}:
            return 0
        if not task:
            continue
        mcp_runtime = build_mcp_runtime(config)
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        trace = TraceWriter(Path("runs") / f"{run_id}.jsonl")
        try:
            agent = Agent(
                model=model,
                tools=ToolRegistry(
                    Path("."),
                    config.permissions,
                    external_tools=mcp_runtime.tools,
                    external_handlers=mcp_runtime.handlers,
                    external_approval_modes=mcp_runtime.approval_modes,
                    approval_callback=None,
                ),
                trace=trace,
                max_steps=config.agent.max_steps,
                workspace=Path("."),
                context_chars=config.agent.context_chars,
            )
            result = agent.run(task)
            print(result.summary)
            print(f"Trace: {trace.path}")
        finally:
            mcp_runtime.close()


def _init_config(force: bool) -> int:
    target = Path("och.config.toml")
    if target.exists() and not force:
        print("och.config.toml already exists. Use --force to overwrite.", file=sys.stderr)
        return 2
    shutil.copyfile(Path("och.config.example.toml"), target)
    print("Created och.config.toml")
    return 0


def _print_trace(path: Path) -> int:
    if not path.exists():
        print(f"Trace not found: {path}", file=sys.stderr)
        return 2
    print(path.read_text(encoding="utf-8"))
    return 0


def _run_eval(suite: Path, config: HarnessConfig, output_dir: Path) -> int:
    report = run_eval_suite(suite, config, output_dir)
    print(report.to_json())
    return 0 if report.passed == report.total else 2


def _replay_trace(path: Path, summary_only: bool, show_content: bool) -> int:
    if not path.exists():
        print(f"Trace not found: {path}", file=sys.stderr)
        return 2
    events = load_trace(path)
    summary = summarize_trace(events)
    if summary_only:
        print(render_summary(summary))
    else:
        print(render_timeline(events, show_content=show_content))
        print()
        print(render_summary(summary))
    return 0


def _compare_reports(paths: list[Path], output: Path | None) -> int:
    reports = [load_eval_report(path) for path in paths]
    markdown = compare_eval_reports(reports)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(markdown)
    return 0


def _run_lab_compare(
    suite: Path,
    presets: list[str],
    config: HarnessConfig,
    output_dir: Path,
    comparison_output: Path,
    skip_missing_keys: bool,
) -> int:
    result = run_provider_comparison(
        suite,
        presets,
        config,
        output_dir,
        comparison_output,
        skip_missing_keys=skip_missing_keys,
    )
    print(result.to_json())
    return 0
