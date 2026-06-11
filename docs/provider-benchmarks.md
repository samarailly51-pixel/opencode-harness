# Provider Benchmark Guide

This guide defines the v0.1 provider benchmark flow for OpenCode Harness.

The benchmark is intentionally reproducible: every provider uses the same agent loop, tools, permissions, trace format, eval runner, and report/dashboard surface.

For a public no-key smoke benchmark, see [v0.1 mock smoke benchmark](../benchmarks/v0.1-mock-smoke/README.md). That report validates the harness and artifact surfaces, but it is not a model-quality ranking.

## Presets

| Preset | Required Env |
| --- | --- |
| `deepseek` | `DEEPSEEK_API_KEY` |
| `qwen` | `DASHSCOPE_API_KEY` |
| `openai` | `OPENAI_API_KEY` |
| `claude` | `ANTHROPIC_API_KEY` |
| `local-openai` | `LOCAL_MODEL_API_KEY` |
| `vllm` | `VLLM_API_KEY` |
| `sglang` | `SGLANG_API_KEY` |
| `ollama` | `OLLAMA_API_KEY` |

For local servers that do not require auth, set the matching key to `dummy`.

## Offline Baseline

Run the mock baseline first:

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

## Hosted Provider Comparison

Run DeepSeek, Qwen, OpenAI, and Claude on the same suite:

```powershell
$env:DEEPSEEK_API_KEY = "..."
$env:DASHSCOPE_API_KEY = "..."
$env:OPENAI_API_KEY = "..."
$env:ANTHROPIC_API_KEY = "..."

python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-suite.json `
  --presets deepseek qwen openai claude `
  --max-steps 8 `
  --context-chars 8000 `
  --comparison-output model-labs/deepseek/reports/provider-comparison.md
```

## Local Provider Comparison

Start your local OpenAI-compatible server, then run:

```powershell
$env:LOCAL_MODEL_API_KEY = "dummy"
$env:VLLM_API_KEY = "dummy"
$env:SGLANG_API_KEY = "dummy"
$env:OLLAMA_API_KEY = "dummy"

python -m opencode_harness lab-compare `
  model-labs/local/local-coding-agent-suite.json `
  --presets local-openai vllm sglang ollama `
  --max-steps 8 `
  --context-chars 8000 `
  --comparison-output model-labs/local/reports/provider-comparison.md
```

## Artifacts To Save

- `eval-runs/**/report.json`
- `eval-runs/**/report.md`
- `eval-runs/**/report.html`
- `eval-runs/**/*.jsonl`
- `model-labs/*/reports/*.md`
- `model-labs/*/reports/*.json`
- `eval-runs/dashboard.html`

## Release Acceptance

Before cutting a release:

- Unit tests pass.
- Mock eval passes.
- At least one provider comparison has a committed or attached `provider-comparison.md`.
- Dashboard renders from the eval artifacts.
- No API keys or secrets are committed.
