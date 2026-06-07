# Changelog

## 0.1.0

Initial clean-room OpenCode Harness release.

### Added

- Model-agnostic coding-agent runtime for Claude Code-class workflows.
- Provider presets for DeepSeek, Qwen, OpenAI, Claude, local OpenAI-compatible endpoints, vLLM, SGLang, Ollama, and mock mode.
- Native OpenAI-compatible tool calls, native Anthropic tool use, and JSON fallback tool protocol.
- Permission-gated file, shell, patch, repository map, context pack, todo, and finish tools.
- Stdio MCP runtime with `initialize`, `tools/list`, `tools/call`, resource list/read, prompt list/get, per-server approvals, lifecycle diagnostics, and tool namespace collision handling.
- JSONL traces with provider transcripts, replay summaries, terminal timeline viewer, HTML trace viewer, and eval dashboard.
- Eval runner with JSON, Markdown, and HTML reports plus failure taxonomy.
- DeepSeek, Qwen, Claude, OpenAI, and Local Model Labs.
- GitHub Actions CI, release package build workflow, and manual model-eval workflow example.

### Clean-Room Boundary

This release does not contain, derive from, or depend on leaked or proprietary Claude Code source code.
