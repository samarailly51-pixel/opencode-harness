# DeepSeek Lab

DeepSeek Lab is the first model-focused track for OpenCode Harness.

It studies DeepSeek V4-class models as first-class backends for Claude Code-class coding agents. The goal is not to reverse engineer private implementation details. The goal is to evaluate public/provider behavior in a reproducible harness.

## Scope

- DeepSeek V4 / V4 Flash / V3.2 / R1 behavior comparison.
- Official API vs compatible providers vs local deployments.
- Coding-agent task success rate.
- Native tool-calling and JSON fallback stability.
- Long-context behavior.
- Chinese coding task quality.
- Cost, latency, and step count reporting.
- Provider template or truncation differences inferred from observable behavior.

## Run

Use the mock provider for lab wiring smoke testing:

```powershell
python -m opencode_harness eval model-labs/deepseek/mock-smoke-suite.json --preset mock --max-steps 2
```

Use DeepSeek-compatible API:

```powershell
$env:DEEPSEEK_API_KEY = "..."
python -m opencode_harness eval model-labs/deepseek/deepseek-v4-suite.json --preset deepseek --max-steps 8
```

Provider-specific configs can override model names, base URLs, context size, and permissions.

## Outputs

Eval runs write per-case traces, sessions, `report.json`, `report.md`, and `report.html` under `eval-runs/`.

Use replay to inspect individual traces:

```powershell
python -m opencode_harness replay eval-runs/<run>/<case>.jsonl --show-content
```

Compare provider runs:

```powershell
python -m opencode_harness compare `
  eval-runs/deepseek-official/report.json `
  eval-runs/local-vllm/report.json `
  eval-runs/siliconflow/report.json `
  --output model-labs/deepseek/reports/provider-comparison.md
```

Or run the same suite across provider presets and produce the comparison report in one command:

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-suite.json `
  --presets deepseek qwen openai claude `
  --max-steps 8 `
  --context-chars 8000 `
  --comparison-output model-labs/deepseek/reports/provider-comparison.md
```

By default, providers with missing API key environment variables are skipped and listed in the generated comparison. Add `--include-missing-keys` when you want missing credentials to fail loudly.

## Clean-Room Boundary

This lab only uses public model APIs, public model metadata, local deployments with authorized weights, and observable runtime behavior. It does not use leaked, proprietary, or unauthorized source code.
