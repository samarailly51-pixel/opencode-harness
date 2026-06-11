# Promo Video Script

Target length: 75 seconds.

## Positioning

OpenCode Harness is an open-source, clean-room evaluation harness for coding agents across DeepSeek, Qwen, Claude, OpenAI, and local models.

## Storyboard

### 0-8s: Problem

Voiceover:

```text
Coding agents are everywhere, but comparing them is messy. Each demo uses different tools, different prompts, and different traces.
```

Visual:

- Quick cuts of provider names: DeepSeek, Qwen, Claude, OpenAI, Local Models.
- Overlay: "Same task? Different runtime. Hard to compare."

### 8-18s: Product Reveal

Voiceover:

```text
OpenCode Harness gives coding agents a shared runtime: one agent loop, one tool layer, one trace format, and one eval surface.
```

Visual:

- Show the website hero.
- Show the command: `python -m opencode_harness eval examples/mock-suite.json --preset mock`.

### 18-34s: Runtime

Voiceover:

```text
Run the same workflow across DeepSeek, Qwen, Claude, OpenAI, vLLM, SGLang, Ollama, and any OpenAI-compatible local endpoint.
```

Visual:

- Provider row.
- Agent loop diagram: task -> model -> tools -> trace -> report.

### 34-50s: Tools and MCP

Voiceover:

```text
The harness includes permissioned file, patch, shell, repo-map, context, todo, and finish tools. It also supports MCP tools, resources, prompts, diagnostics, and per-server approvals.
```

Visual:

- Tool list animation.
- MCP server connected to tools/resources/prompts.

### 50-64s: Evaluation Surface

Voiceover:

```text
Every run produces JSONL traces, provider transcripts, replay summaries, HTML reports, a terminal trace viewer, and an eval dashboard.
```

Visual:

- Show `site/assets/trace-preview.png`.
- Show `site/assets/dashboard-preview.png`.

### 64-75s: Call To Action

Voiceover:

```text
OpenCode Harness v0.1.0 is open source now. Use it to test, compare, and debug coding agents across model providers.
```

Visual:

- GitHub repo URL.
- Release badge.
- Final line: "Run the same coding-agent workflow everywhere."

## Short Product Hunt Video Caption

```text
OpenCode Harness is a clean-room eval harness for coding agents. Run the same workflow across DeepSeek, Qwen, Claude, OpenAI, and local models, then inspect traces, tool calls, transcripts, and dashboards.
```

## Recording Checklist

- Website hero.
- Terminal running mock eval.
- Terminal trace viewer.
- HTML trace viewer.
- Eval dashboard.
- GitHub release page.

For a repeatable recording workflow, use [video-production-kit.md](video-production-kit.md).
