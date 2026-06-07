# Architecture

OpenCode Harness is a clean-room runtime for Claude Code-class coding agents.

It is inspired by publicly observable coding-agent workflows and legal open-source agent systems. It does not contain, derive from, or depend on leaked or proprietary Claude Code source code.

## Runtime Loop

```text
task
  -> context builder
  -> model router
  -> model response
  -> tool call parser
  -> permission gate
  -> tool execution
  -> trace event
  -> observation
  -> next model call
  -> finish
```

## Modules

- `config.py`: typed harness configuration.
- `providers.py`: provider presets for DeepSeek, Qwen, OpenAI, Claude, and mock mode.
- `models.py`: model adapters. OpenAI-compatible endpoints cover DeepSeek, Qwen, OpenAI, vLLM, SGLang, Ollama bridges, and similar servers.
- `repo_map.py`: repository discovery, lightweight symbol extraction, and context packing.
- `tool_schemas.py`: provider-neutral tool definitions rendered as OpenAI-compatible and Anthropic tool schemas.
- `mcp.py`: MCP-compatible external tool metadata and handler extension types.
- `agent.py`: step-based agent loop and tool-call parsing.
- `tools.py`: workspace tools for files, search, shell, git diff, and guarded edits.
- `permissions.py`: conservative policy checks for shell and file operations.
- `trace.py`: JSONL trace writer for replay, audit, and evaluation.
- `replay.py`: trace reader, timeline renderer, and summary statistics.
- `session.py`: resumable session state, messages, steps, status, and todos.
- `eval.py`: JSON eval suite runner with per-case traces, sessions, and reports.
- `cli.py`: command-line entrypoint.

## Tool Protocol

The MVP uses a provider-neutral JSON tool-call protocol. A model can ask for exactly one tool call by returning:

```json
{"tool": "read_file", "args": {"path": "README.md"}}
```

This avoids early dependence on any provider-specific function-calling format. Native tool-calling adapters can be added later.

OpenAI-compatible providers can receive native `tools` schemas. If a response contains `tool_calls`, the agent executes the first tool call directly.

Anthropic providers can receive native `tools` schemas. If a response contains `tool_use` content blocks, the agent executes the first tool call directly.

If no native call is present, the agent falls back to the JSON text protocol.

## MCP-Compatible Extension Points

External tools can be declared with `[[mcp_tools]]` in config. These declarations are rendered into the same native tool schemas as built-in tools, so OpenAI-compatible and Anthropic providers can request them.

`ToolRegistry` accepts:

- `external_tools`: metadata for declared tools
- `external_handlers`: runtime callables keyed by tool name

This creates a stable extension point for MCP clients and built-in stdio MCP process management.

The stdio MCP client layer supports:

- process startup from `[[mcp_servers]]`
- `initialize`
- `notifications/initialized`
- `tools/list`
- `tools/call`

Discovered MCP tools are added to the same external tool registry and provider-native schemas as statically declared tools.

## Safety Boundary

File writes are disabled by default. Use `--allow-write` or `allow_write = true` to enable:

- `write_file`
- `replace_text`
- `apply_patch`

Alternatively, set `approval_mode = "ask"` or pass `--approval-mode ask` to prompt before a blocked write, blocked shell command, or MCP-compatible external tool call. The default `approval_mode = "never"` keeps non-allowlisted operations blocked without prompting.

Todo tools mutate session state:

- `todo_set`
- `todo_list`

Repository tools summarize codebase structure:

- `repo_map`
- `context_pack`

Shell commands are also policy-gated. The classifier rejects empty commands, compound shell syntax such as `&&` and `|`, shell redirection, network-like commands, and write-like commands before checking the read-only allowlist. The default allowlist covers common inspection and test commands such as `git status`, `git diff`, `git show`, `rg`, `ls`, `dir`, `pytest`, and `python -m unittest`.

## Session State

Each run can write a session JSON file with:

- task
- step count
- status
- message history
- todo list

Use `--session path/to/session.json` to choose a session path. Use `--resume` to continue from an existing session.

## Repository Context

New sessions receive an initial packed repository context before the task message. The packer:

- ignores common generated directories such as `.git`, `node_modules`, `runs`, and caches
- identifies language by extension
- extracts lightweight symbols from Python, JavaScript, TypeScript, and Markdown
- prioritizes files matching task terms

Use `context_chars = 0` or `--context-chars 0` to disable automatic context injection.

## Eval Runner

Eval suites are JSON files containing independent cases. Each case specifies:

- `id`
- `task`
- `workspace`
- optional `expect_contains`

The runner executes every case with the same model/config and writes:

- per-case trace JSONL
- per-case session JSON
- suite-level `report.json`
- suite-level `report.md`
- suite-level `report.html`

This is the first layer for comparing DeepSeek, Qwen, Claude, OpenAI, and local models on identical coding-agent tasks.

`compare` loads multiple `report.json` files or eval run directories and renders a Markdown comparison table with pass rate, average steps, total seconds, and per-case status.

## Trace Replay

Trace replay does not call a model or execute tools. It reads JSONL trace events and renders:

- task start/finish
- model responses
- tool calls and status
- context packing events
- summary statistics

This supports debugging, audit trails, and later UI/report generation.

## Provider Strategy

Current presets:

- `deepseek`: OpenAI-compatible API with `DEEPSEEK_API_KEY`.
- `qwen`: DashScope OpenAI-compatible mode with `DASHSCOPE_API_KEY`.
- `openai`: OpenAI API with `OPENAI_API_KEY`.
- `claude`: Anthropic Messages API with `ANTHROPIC_API_KEY`.
- `mock`: offline model for tests and demos.

## Near-Term Roadmap

1. Add MCP resource/list/read support.
2. Add provider-specific transcript adapters for exact replay.
3. Add first-class failure taxonomy.
4. Add TUI or HTML trace viewer.
5. Add MCP prompt support.
