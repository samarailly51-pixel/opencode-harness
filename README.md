# OpenCode Harness

[![CI](https://github.com/samarailly51-pixel/opencode-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/samarailly51-pixel/opencode-harness/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

OpenCode Harness is a clean-room, model-agnostic runtime for Claude Code-class coding agents.

It is designed to run coding workflows with DeepSeek, Qwen, Claude, OpenAI, local OpenAI-compatible servers, and future providers through a shared agent loop, tool layer, permission model, and trace format.

This project does not contain or derive from Claude Code source code. It is an independent implementation of a coding-agent harness.

## MVP Scope

- CLI for running a coding-agent task against a workspace.
- Pluggable model interface.
- OpenAI-compatible chat-completions adapter for DeepSeek, Qwen, OpenAI, vLLM, SGLang, Ollama bridges, and similar endpoints.
- Built-in mock model for offline testing.
- Tool layer for file reads, file search, patch application, shell commands, and git diff.
- Repository map and context packing for larger codebases.
- Native OpenAI-compatible and Anthropic tool schemas with JSON text fallback.
- MCP-compatible external tool extension points.
- Permission policy that defaults to conservative command execution.
- JSONL trace files for replay, evaluation, and debugging.

## Quick Start

Run the offline mock agent:

```powershell
python -m opencode_harness chat --mock
```

Run a one-shot task with an OpenAI-compatible endpoint:

```powershell
$env:OCH_API_KEY = "..."
python -m opencode_harness run "inspect this repository and suggest the first improvement" `
  --provider openai-compatible `
  --base-url "https://api.deepseek.com" `
  --model "deepseek-chat"
```

Use a provider preset:

```powershell
$env:DEEPSEEK_API_KEY = "..."
python -m opencode_harness run "inspect this repository" --preset deepseek

$env:DASHSCOPE_API_KEY = "..."
python -m opencode_harness run "inspect this repository" --preset qwen

$env:OPENAI_API_KEY = "..."
python -m opencode_harness run "inspect this repository" --preset openai

$env:ANTHROPIC_API_KEY = "..."
python -m opencode_harness run "inspect this repository" --preset claude
```

Or use provider config examples:

```powershell
python -m opencode_harness run "inspect this repository" --config examples/providers/deepseek.toml
python -m opencode_harness run "inspect this repository" --config examples/providers/qwen.toml
python -m opencode_harness run "inspect this repository" --config examples/providers/local-openai-compatible.toml
```

Allow file edits explicitly:

```powershell
python -m opencode_harness run "update the README title" --preset deepseek --allow-write
```

Save or resume a session:

```powershell
python -m opencode_harness run "fix the failing test" --preset deepseek --session runs/fix.session.json
python -m opencode_harness run "continue" --preset deepseek --session runs/fix.session.json --resume
```

Create a sample config:

```powershell
python -m opencode_harness init
```

## Configuration

`och.config.example.toml`:

```toml
[model]
provider = "openai-compatible"
base_url = "https://api.deepseek.com"
model = "deepseek-chat"
api_key_env = "OCH_API_KEY"

[agent]
max_steps = 8
context_chars = 6000

[permissions]
allow_write = false
allow_shell = true
allow_network = false

[[mcp_tools]]
name = "mcp_lookup"
description = "Example external MCP-compatible lookup tool."
server = "docs"

[mcp_tools.input_schema]
type = "object"

[[mcp_servers]]
name = "docs"
command = "python"
args = ["path/to/mcp_server.py"]
```

## Commands

```powershell
python -m opencode_harness run "fix the failing test"
python -m opencode_harness chat --mock
python -m opencode_harness trace runs/latest.jsonl
python -m opencode_harness replay runs/latest.jsonl
python -m opencode_harness init
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2
```

Provider presets:

- `deepseek`: OpenAI-compatible, `https://api.deepseek.com`, `DEEPSEEK_API_KEY`
- `qwen`: OpenAI-compatible DashScope mode, `DASHSCOPE_API_KEY`
- `openai`: OpenAI API, `OPENAI_API_KEY`
- `claude`: Anthropic Messages API, `ANTHROPIC_API_KEY`
- `mock`: offline model for harness tests

## Tool Protocol

Models can request tools with provider-neutral JSON:

```json
{"tool": "todo_set", "args": {"items": [{"title": "inspect tests", "status": "in_progress"}]}}
```

```json
{"tool": "apply_patch", "args": {"patch": "--- a/file.txt\n+++ b/file.txt\n@@ -1,1 +1,1 @@\n-old\n+new"}}
```

`apply_patch`, `write_file`, and `replace_text` require `--allow-write`.

OpenAI-compatible and Anthropic providers also receive native tool schemas. If the provider returns `tool_calls` or Anthropic `tool_use` blocks, the agent uses them directly; otherwise it falls back to the JSON text protocol above.

External MCP-compatible tools can be declared in config and are included in native tool schemas:

```toml
[[mcp_tools]]
name = "mcp_lookup"
description = "Lookup from an MCP server."
server = "docs"

[mcp_tools.input_schema]
type = "object"
```

At runtime, external tools are dispatched through `ToolRegistry` handlers. If a tool is declared but no client/handler is attached, the harness returns a clear tool error instead of pretending it ran.

Stdio MCP servers can be configured with `[[mcp_servers]]`. The harness starts the process, sends `initialize`, reads `tools/list`, and dispatches calls through `tools/call`:

```toml
[[mcp_servers]]
name = "docs"
command = "python"
args = ["path/to/mcp_server.py"]
```

Repository context tools:

```json
{"tool": "repo_map", "args": {}}
```

```json
{"tool": "context_pack", "args": {"query": "auth failing test"}}
```

The agent also injects an initial packed repository context into new sessions. Control its size with:

```powershell
python -m opencode_harness run "fix auth tests" --preset deepseek --context-chars 8000
```

## Eval Suites

Eval suites are JSON files:

```json
{
  "name": "repo smoke",
  "cases": [
    {
      "id": "inspect-repo",
      "task": "inspect this repo",
      "workspace": ".",
      "expect_contains": "summary text"
    }
  ]
}
```

Run a suite:

```powershell
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2
```

Each case writes its own trace and session under `eval-runs/`. The runner also writes a `report.json` with pass/fail status, timing, steps, summary, and artifact paths.

## Model Labs

Model Labs are focused tracks for evaluating model families inside the same harness.

- [DeepSeek Lab](model-labs/deepseek/README.md): DeepSeek V4-class behavior, provider comparison, tool-calling stability, coding-agent evals, and Chinese coding tasks.

## Trace Replay

Print a readable timeline:

```powershell
python -m opencode_harness replay runs/latest.jsonl
```

Print only summary stats:

```powershell
python -m opencode_harness replay runs/latest.jsonl --summary
```

Show full model and tool content:

```powershell
python -m opencode_harness replay runs/latest.jsonl --show-content
```

## Design Principles

- Clean-room implementation.
- Model-neutral provider layer.
- DeepSeek and Qwen are first-class targets through OpenAI-compatible APIs.
- Trace everything that matters: prompt, tool call, command output, file edits, model parameters, and timing.
- Prefer reproducibility and auditability over hidden automation.

## Project Docs

- [Architecture](docs/architecture.md)
- [GitHub readiness checklist](docs/github-readiness.md)
- [Release guide](docs/release.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [License](LICENSE)
