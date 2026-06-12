# OpenCode Harness

[![CI](https://github.com/samarailly51-pixel/opencode-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/samarailly51-pixel/opencode-harness/actions/workflows/ci.yml)
[![Pages](https://github.com/samarailly51-pixel/opencode-harness/actions/workflows/pages.yml/badge.svg)](https://github.com/samarailly51-pixel/opencode-harness/actions/workflows/pages.yml)
[![Release](https://img.shields.io/github/v/release/samarailly51-pixel/opencode-harness?display_name=tag)](https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

OpenCode Harness is a clean-room, model-neutral runtime and evaluation harness for coding agents.

It runs the same coding-agent workflow across DeepSeek, Qwen, Claude, OpenAI, local OpenAI-compatible servers, vLLM, SGLang, Ollama, and future providers through one shared agent loop, tool layer, permission model, trace format, and eval surface.

This project does not contain or derive from Claude Code source code. It is an independent implementation of a coding-agent harness.

- **Website:** [samarailly51-pixel.github.io/opencode-harness](https://samarailly51-pixel.github.io/opencode-harness/)
- **Release:** [v0.1.0](https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0)
- **Demo report:** [v0.1 mock smoke benchmark](benchmarks/v0.1-mock-smoke/README.md)
- **Demo video:** [media/demo-video](media/demo-video/README.md)
- **Launch status:** [readiness dashboard](docs/launch-readiness.md)
- **Launch assets:** [Product Hunt final package](docs/product-hunt-final-package.md), [video production kit](docs/video-production-kit.md)

![OpenCode Harness dashboard preview](site/assets/dashboard-preview.png)

## Quick Demo

Run the offline mock eval with no API key:

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
```

Inspect the run:

```powershell
$trace = Get-ChildItem eval-runs -Recurse -Filter inspect-repo.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
python -m opencode_harness tui $trace.FullName --width 88
python -m opencode_harness trace-html $trace.FullName --output eval-runs/latest-trace.html
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

Or generate all recording/demo artifacts:

```powershell
.\scripts\recording-demo.ps1
```

## What You Get

- Model-neutral provider presets for DeepSeek, Qwen, Claude, OpenAI, vLLM, SGLang, Ollama, local OpenAI-compatible endpoints, and mock mode.
- Permissioned file, patch, shell, search, repo-map, context-pack, todo, and finish tools.
- MCP-compatible extension points for stdio tools, resources, prompts, diagnostics, and per-server approvals.
- JSONL traces, provider transcripts, terminal replay, HTML trace viewer, eval reports, comparison reports, and dashboards.
- Model Labs for DeepSeek, Qwen, Claude, OpenAI, and local providers.

## Why It Exists

Most coding-agent demos are tied to one model, one provider, or one UI. OpenCode Harness focuses on the infrastructure layer: run the same coding-agent loop across multiple providers, preserve auditable traces, gate risky tools, and compare model behavior with reproducible evals.

## v0.1 Status

- Released: [v0.1.0](https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0)
- Website: [OpenCode Harness](https://samarailly51-pixel.github.io/opencode-harness/)
- Package artifacts: wheel and source distribution attached to the release.
- CI: Python 3.11/3.12 tests and mock eval smoke.
- Model Labs: DeepSeek, Qwen, Claude, OpenAI, and Local Model Labs.
- Product surface: CLI, trace replay, terminal trace viewer, HTML trace viewer, eval dashboard, release workflow, and model-eval workflow example.

## Core Capabilities

- CLI for running a coding-agent task against a workspace.
- Pluggable model interface.
- OpenAI-compatible chat-completions adapter for DeepSeek, Qwen, OpenAI, vLLM, SGLang, Ollama bridges, and similar endpoints.
- Built-in mock model for offline testing.
- Tool layer for file reads, file search, patch application, shell commands, and git diff.
- Repository map and context packing for larger codebases.
- Native OpenAI-compatible and Anthropic tool schemas with JSON text fallback.
- MCP-compatible external tool extension points.
- Permission policy that defaults to conservative command execution.
- JSONL trace files with provider transcripts for replay, evaluation, and debugging.

## Showcase

| Surface | Output |
| --- | --- |
| Website | <https://samarailly51-pixel.github.io/opencode-harness/> |
| Release | <https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0> |
| Public demo report | [benchmarks/v0.1-mock-smoke](benchmarks/v0.1-mock-smoke/README.md) |
| Demo video | [media/demo-video](media/demo-video/README.md) |
| Launch readiness | [docs/launch-readiness.md](docs/launch-readiness.md) |
| Product Hunt final package | [docs/product-hunt-final-package.md](docs/product-hunt-final-package.md) |
| Run offline demo | `python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2` |
| Terminal trace viewer | `python -m opencode_harness tui runs/latest.jsonl` |
| HTML trace viewer | `python -m opencode_harness trace-html runs/latest.jsonl --output runs/latest.html` |
| Eval dashboard | `python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html` |
| Launch kit | [docs/launch-kit.md](docs/launch-kit.md) |

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

$env:LOCAL_MODEL_API_KEY = "dummy"
python -m opencode_harness run "inspect this repository" --preset local-openai --model "your-local-model"
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

Ask before running blocked shell commands, writes, or MCP tool calls:

```powershell
python -m opencode_harness run "fix the failing test" --preset deepseek --approval-mode ask
```

Shell commands are classified before execution. Common read-only inspection commands such as `git status`, `git diff`, `rg`, `ls`, `dir`, `pytest`, and `python -m unittest` are allowed by default. Compound commands, redirection, network commands, and write-like commands require approval or remain blocked.

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
approval_mode = "never"

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
approval_mode = "inherit"
```

## Commands

```powershell
python -m opencode_harness run "fix the failing test"
python -m opencode_harness version
python -m opencode_harness chat --mock
python -m opencode_harness trace runs/latest.jsonl
python -m opencode_harness replay runs/latest.jsonl
python -m opencode_harness tui runs/latest.jsonl
python -m opencode_harness trace-html runs/latest.jsonl --output runs/latest.html
python -m opencode_harness init
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

Provider presets:

- `deepseek`: OpenAI-compatible, `https://api.deepseek.com`, `DEEPSEEK_API_KEY`
- `qwen`: OpenAI-compatible DashScope mode, `DASHSCOPE_API_KEY`
- `openai`: OpenAI API, `OPENAI_API_KEY`
- `claude`: Anthropic Messages API, `ANTHROPIC_API_KEY`
- `local-openai`: local OpenAI-compatible endpoint, `LOCAL_MODEL_API_KEY`
- `vllm`: local vLLM OpenAI-compatible endpoint, `VLLM_API_KEY`
- `sglang`: local SGLang OpenAI-compatible endpoint, `SGLANG_API_KEY`
- `ollama`: local Ollama OpenAI-compatible endpoint, `OLLAMA_API_KEY`
- `mock`: offline model for harness tests

## Tool Protocol

Models can request tools with provider-neutral JSON:

```json
{"tool": "todo_set", "args": {"items": [{"title": "inspect tests", "status": "in_progress"}]}}
```

```json
{"tool": "apply_patch", "args": {"patch": "--- a/file.txt\n+++ b/file.txt\n@@ -1,1 +1,1 @@\n-old\n+new"}}
```

`apply_patch`, `write_file`, and `replace_text` require `--allow-write`, unless `--approval-mode ask` is enabled and the user approves the specific write.

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

At runtime, external tools are dispatched through `ToolRegistry` handlers. If `approval_mode = "ask"` is enabled, each MCP-compatible external tool call is approved before dispatch. If a tool is declared but no client/handler is attached, the harness returns a clear tool error instead of pretending it ran.

Stdio MCP servers can be configured with `[[mcp_servers]]`. The harness starts the process, sends `initialize`, reads `tools/list`, and dispatches calls through `tools/call`:

```toml
[[mcp_servers]]
name = "docs"
command = "python"
args = ["path/to/mcp_server.py"]
approval_mode = "inherit"
```

Discovered MCP tools are exposed to the model as native OpenAI-compatible or Anthropic tool schemas. If two servers expose the same tool name, later collisions are safely namespaced as `mcp_<server>_<tool>`.

Each MCP server also receives utility tools:

- `mcp_<server>_list_resources`
- `mcp_<server>_read_resource`
- `mcp_<server>_list_prompts`
- `mcp_<server>_get_prompt`
- `mcp_<server>_status`

Set per-server `approval_mode` to `inherit`, `ask`, or `never`. `inherit` follows the global approval mode; `ask` requires approval for that server's MCP calls even if global approval is `never`.

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

Each case writes its own trace and session under `eval-runs/`. The runner also writes `report.json`, `report.md`, and `report.html` with pass/fail status, failure type, timing, steps, summaries, and artifact paths.

Failure types include `exception`, `tool_failure`, `max_steps`, `expectation_mismatch`, `verification_failure`, and `recovered_tool_failure`.

Render an eval dashboard:

```powershell
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

Compare multiple eval reports:

```powershell
python -m opencode_harness compare `
  eval-runs/deepseek-run/report.json `
  eval-runs/qwen-run/report.json `
  --output eval-runs/model-comparison.md
```

Comparisons include pass rate, failure breakdown, average steps, total seconds, and a per-case matrix.

Run one eval suite across provider presets:

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-suite.json `
  --presets deepseek qwen openai claude `
  --comparison-output model-labs/deepseek/reports/provider-comparison.md
```

DeepSeek Lab also includes a long-context suite:

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-long-context-suite.json `
  --presets deepseek qwen openai claude `
  --context-chars 24000 `
  --comparison-output model-labs/deepseek/reports/long-context-comparison.md
```

Repair suites can copy fixture workspaces into an eval run, allow the agent to edit the copy, and verify the result with a command:

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-repair-suite.json `
  --presets deepseek qwen openai claude `
  --allow-write `
  --comparison-output model-labs/deepseek/reports/repair-comparison.md
```

## Model Labs

Model Labs are focused tracks for evaluating model families inside the same harness.

- [DeepSeek Lab](model-labs/deepseek/README.md): DeepSeek V4-class behavior, provider comparison, tool-calling stability, coding-agent evals, and Chinese coding tasks.
- [Qwen Lab](model-labs/qwen/README.md): Qwen provider behavior, Chinese coding tasks, tool-calling stability, JSON fallback discipline, and provider comparison.
- [Claude Lab](model-labs/claude/README.md): Anthropic native tool use, Claude provider behavior, repair readiness, context synthesis, and provider comparison.
- [OpenAI Lab](model-labs/openai/README.md): OpenAI-compatible baseline behavior, native tool calls, transcript auditability, context synthesis, and provider comparison.
- [Local Model Lab](model-labs/local/README.md): vLLM, SGLang, Ollama, and local OpenAI-compatible endpoint behavior, transcript auditability, and provider comparison.

## Trace Replay

Print a readable timeline:

```powershell
python -m opencode_harness replay runs/latest.jsonl
```

Print only summary stats:

```powershell
python -m opencode_harness replay runs/latest.jsonl --summary
```

Render a terminal timeline viewer:

```powershell
python -m opencode_harness tui runs/latest.jsonl
```

Render a standalone HTML trace viewer:

```powershell
python -m opencode_harness trace-html runs/latest.jsonl --output runs/latest.html
```

Show full model and tool content:

```powershell
python -m opencode_harness replay runs/latest.jsonl --show-content
```

Model response events include provider-specific transcripts for mock, OpenAI-compatible, and Anthropic adapters. These transcripts capture the provider request payload and raw response body, excluding API key headers, so eval runs can be audited and replay tooling can reconstruct exact provider calls.

## Packaging

The package exposes `och` and `opencode-harness` console scripts:

```powershell
python -m pip install .
och version
och --help
```

Build release artifacts locally:

```powershell
python -m pip install build
python -m build
```

The repository includes a tag/manual release workflow that builds wheel and source distributions, plus a manual model-evals workflow example that uploads eval artifacts.

Use the reproducible v0.1 demo flow in [examples/release-demo](examples/release-demo/README.md) to generate trace, report, and dashboard artifacts locally.

The static landing page lives in [site](site/README.md). Launch materials live in [docs/launch-kit.md](docs/launch-kit.md), with the first promo video script in [docs/promo-video-script.md](docs/promo-video-script.md).

## Design Principles

- Clean-room implementation.
- Model-neutral provider layer.
- DeepSeek and Qwen are first-class targets through OpenAI-compatible APIs.
- Trace everything that matters: prompt, provider payload, model response, tool call, command output, file edits, model parameters, and timing.
- Prefer reproducibility and auditability over hidden automation.

## Project Docs

- [Architecture](docs/architecture.md)
- [v0.1 mock smoke benchmark](benchmarks/v0.1-mock-smoke/README.md)
- [Launch readiness](docs/launch-readiness.md)
- [Product Hunt final package](docs/product-hunt-final-package.md)
- [Resume positioning](docs/resume-positioning.md)
- [Launch kit](docs/launch-kit.md)
- [Promo video script](docs/promo-video-script.md)
- [Video production kit](docs/video-production-kit.md)
- [Website deployment](docs/website-deployment.md)
- [Provider benchmark guide](docs/provider-benchmarks.md)
- [GitHub readiness checklist](docs/github-readiness.md)
- [Release guide](docs/release.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [License](LICENSE)
