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
- [ ] DeepSeek V4 long-context suite.
- [ ] DeepSeek V4 coding-agent repair suite.
- [ ] Qwen Lab.
- [ ] Claude Lab.
- [ ] OpenAI Lab.
- [ ] Local model lab for vLLM/SGLang/Ollama-compatible endpoints.

## 0.4 MCP

- [ ] MCP resource list/read support.
- [ ] MCP prompt support.
- [ ] Per-server permissions.
- [ ] Server lifecycle diagnostics.
- [ ] Tool namespace collision handling.

## 0.5 Product Surface

- [ ] TUI timeline viewer.
- [ ] HTML trace viewer.
- [ ] Eval dashboard.
- [ ] Packaged CLI release.
- [ ] Example GitHub workflows for model evals.

## Principles

- Clean-room implementation.
- Model-neutral architecture.
- DeepSeek and Qwen as first-class provider targets.
- Traceable and reproducible runs.
- Permissioned tools by default.
- No leaked or proprietary source-code dependencies.
