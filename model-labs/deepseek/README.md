# DeepSeek Lab

DeepSeek Lab is the first model-focused track for OpenCode Harness.

It studies DeepSeek V4-class models as first-class backends for Claude Code-class coding agents. The goal is not to reverse engineer private implementation details. The goal is to evaluate public/provider behavior in a reproducible harness.

Latest published DeepSeek-only snapshot:

| Suite | Result | Main failure modes |
| --- | ---: | --- |
| Smoke | 1/4 passed | `expectation_mismatch` |
| Long context | 1/4 passed | `expectation_mismatch`, `max_steps` |
| Repair | 0/2 passed | `expectation_mismatch` |

See [reports/provider-comparison.md](reports/provider-comparison.md),
[reports/long-context-comparison.md](reports/long-context-comparison.md),
[reports/repair-comparison.md](reports/repair-comparison.md), and the public
[real provider comparison package](../../benchmarks/real-provider-comparison/README.md).

Current direction: DeepSeek-only depth before cross-provider breadth. The next
work is diagnosing the failure modes surfaced by the first full benchmark set.

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

Run the DeepSeek-only benchmark helper:

```powershell
$env:DEEPSEEK_API_KEY = "..."
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet smoke
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet long-context
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet repair
```

Run the long-context suite with a larger repository context budget:

```powershell
$env:DEEPSEEK_API_KEY = "..."
python -m opencode_harness eval `
  model-labs/deepseek/deepseek-v4-long-context-suite.json `
  --preset deepseek `
  --max-steps 10 `
  --context-chars 24000
```

Run the coding-agent repair suite with isolated fixture copies and write permission:

```powershell
$env:DEEPSEEK_API_KEY = "..."
python -m opencode_harness eval `
  model-labs/deepseek/deepseek-v4-repair-suite.json `
  --preset deepseek `
  --max-steps 12 `
  --context-chars 8000 `
  --allow-write
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

For long-context provider comparison, point `lab-compare` at `deepseek-v4-long-context-suite.json` and use a larger `--context-chars` value:

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-long-context-suite.json `
  --presets deepseek qwen openai claude `
  --max-steps 10 `
  --context-chars 24000 `
  --comparison-output model-labs/deepseek/reports/long-context-comparison.md
```

For repair comparison, use the repair suite and enable writes. Each case copies its fixture into the eval run directory before the agent starts, so model edits do not modify the checked-in fixtures. The suite verifies repairs with `python -m unittest discover -s tests -t .` inside each copied workspace.

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-repair-suite.json `
  --presets deepseek qwen openai claude `
  --max-steps 12 `
  --context-chars 8000 `
  --allow-write `
  --comparison-output model-labs/deepseek/reports/repair-comparison.md
```

## Clean-Room Boundary

This lab only uses public model APIs, public model metadata, local deployments with authorized weights, and observable runtime behavior. It does not use leaked, proprietary, or unauthorized source code.
