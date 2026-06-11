# Resume Positioning

This document packages OpenCode Harness as a resume and interview project.

## One-Line Positioning

English:

```text
Built a clean-room, model-agnostic coding-agent harness for evaluating Claude Code-class workflows across DeepSeek, Qwen, Claude, OpenAI, and local LLM providers.
```

Chinese:

```text
独立实现 clean-room coding-agent harness，用统一 agent loop、工具层、权限模型、trace 和 eval suite 对 DeepSeek/Qwen/Claude/OpenAI/本地模型进行行为评测。
```

## Resume Bullets

English:

- Designed and implemented a clean-room coding-agent runtime with provider adapters for DeepSeek, Qwen, OpenAI, Claude, local OpenAI-compatible endpoints, vLLM, SGLang, Ollama, and mock mode.
- Built a permission-gated tool layer for file reads/writes, search, patch application, shell execution, git diff, repository mapping, context packing, todos, and task finalization.
- Implemented native OpenAI-compatible tool calls, native Anthropic tool use, and JSON fallback parsing behind a provider-neutral tool protocol.
- Added session resume, JSONL trace capture, provider transcript recording, replay summaries, terminal trace viewer, HTML trace viewer, and eval dashboard.
- Built an MCP-compatible runtime with stdio server lifecycle management, tools, resources, prompts, per-server approvals, diagnostics, and namespace collision handling.
- Created DeepSeek, Qwen, Claude, OpenAI, and Local Model Labs with reproducible eval suites, provider-comparison reports, release workflow, and model-eval GitHub Actions examples.

Chinese:

- 独立设计并实现 clean-room coding-agent runtime，支持 DeepSeek、Qwen、OpenAI、Claude、本地 OpenAI-compatible endpoint、vLLM、SGLang、Ollama 与 mock provider。
- 构建权限控制工具层，覆盖文件读写、搜索、patch、shell、git diff、repo map、context pack、todo 和任务完成流程。
- 实现 OpenAI-compatible native tool calls、Anthropic native tool use 与 JSON fallback 协议，统一不同模型的工具调用行为。
- 实现 session resume、JSONL trace、provider transcript、replay summary、TUI trace viewer、HTML trace viewer 与 eval dashboard。
- 实现 MCP-compatible runtime，支持 stdio server lifecycle、tools、resources、prompts、per-server approvals、diagnostics 和工具命名冲突处理。
- 建立 DeepSeek/Qwen/Claude/OpenAI/Local Model Labs，提供可复现 eval suite、provider comparison report、release workflow 与 model-eval GitHub Actions 示例。

## Short Project Description

OpenCode Harness is an AI developer-tools infrastructure project. It focuses on the runtime and evaluation layer for coding agents: provider routing, native and fallback tool calling, permissioned workspace tools, MCP extension points, trace replay, eval reports, and model-lab comparisons.

## Interview Narrative

1. I started from the problem that coding-agent demos are often provider-specific and hard to compare.
2. I designed a provider-neutral agent loop and tool protocol so DeepSeek, Qwen, Claude, OpenAI, and local models can run the same task surface.
3. I added safety boundaries: writes and risky shell commands are gated, MCP calls can require approval, and traces record model/tool behavior without API key headers.
4. I made the project measurable with eval suites, report comparison, failure taxonomy, model labs, trace viewers, and a dashboard.
5. I shipped it like a real package: CI, GitHub workflows, release artifacts, changelog, provider benchmark guide, and v0.1.0 release.

## Clean-Room Boundary

Do say:

- Clean-room implementation.
- Inspired by publicly observable coding-agent workflows.
- Claude Code-class workflow harness.
- No proprietary or leaked source-code dependency.

Do not say:

- Decompiled Claude Code.
- Reused Claude Code implementation.
- Based on leaked 510k lines.
- Reverse engineered proprietary source.

## Best Fit Roles

- AI infrastructure engineer.
- LLM application engineer.
- Agent framework engineer.
- Developer tooling engineer.
- Platform engineer working on internal AI coding tools.
