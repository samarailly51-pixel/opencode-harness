# Roadmap

OpenCode Harness is a clean-room, model-agnostic runtime for Claude Code-class coding agents.

## 0.1 Foundation

- [x] CLI runtime.
- [x] Model router.
- [x] OpenAI-compatible providers.
- [x] Anthropic provider.
- [x] Native OpenAI-compatible tool calling.
- [x] Native Anthropic tool use.
- [x] JSON text tool fallback.
- [x] Permission-gated file and shell tools.
- [x] Trace JSONL.
- [x] Trace replay.
- [x] Session state and resume.
- [x] Todo tools.
- [x] Repository map and context packing.
- [x] Eval suite runner.
- [x] MCP-compatible external tool declarations.
- [x] Stdio MCP `initialize`, `tools/list`, and `tools/call`.
- [x] DeepSeek Lab.
- [x] GitHub CI and contribution docs.

## 0.2 Reliability

- [x] Richer approval prompts for shell, write, and MCP tool calls.
- [x] Better shell command classification.
- [x] Stronger unified diff parser.
- [x] Provider-specific transcript adapters for exact replay.
- [x] Markdown eval reports.
- [x] Model comparison tables across eval reports.
- [x] HTML eval reports.
- [x] First-class failure taxonomy.

## 0.3 Model Labs

- [x] DeepSeek V4 provider comparison reports.
- [x] DeepSeek V4 long-context suite.
- [x] DeepSeek V4 coding-agent repair suite.
- [x] Qwen Lab.
- [x] Claude Lab.
- [x] OpenAI Lab.
- [x] Local model lab for vLLM/SGLang/Ollama-compatible endpoints.

## 0.4 MCP

- [x] MCP resource list/read support.
- [x] MCP prompt support.
- [x] Per-server permissions.
- [x] Server lifecycle diagnostics.
- [x] Tool namespace collision handling.

## 0.5 Product Surface

- [x] TUI timeline viewer.
- [x] HTML trace viewer.
- [x] Eval dashboard.
- [x] Packaged CLI release.
- [x] Example GitHub workflows for model evals.

## 0.6 v0.1 Release Hardening

- [x] CLI version command.
- [x] Release notes and changelog.
- [x] Provider benchmark runbook.
- [x] Reproducible demo artifact manifest.
- [x] Release workflow install smoke.
- [x] First release tag.

## 0.7 Launch Surface

- [x] Static website.
- [x] GitHub Pages deployment workflow.
- [x] Product Hunt launch kit.
- [x] Product Hunt final submission package.
- [x] Product Hunt gallery and thumbnail assets.
- [x] Promo video script.
- [x] Video production kit and captions.
- [x] Public mock smoke benchmark report.
- [x] Real provider benchmark runner and report package.
- [x] DeepSeek-only benchmark runner.
- [x] Launch readiness dashboard.
- [ ] Recorded demo video.
- [x] Real-provider benchmark report.
- [x] Refreshed DeepSeek smoke report with stable marker-based Chinese task.
- [x] DeepSeek long-context and repair reports.
- [ ] DeepSeek failure-mode diagnosis report.

## Principles

- Clean-room implementation.
- Model-neutral architecture.
- DeepSeek and Qwen as first-class provider targets.
- Traceable and reproducible runs.
- Permissioned tools by default.
- No leaked or proprietary source-code dependencies.
