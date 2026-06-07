# Qwen Lab

Qwen Lab evaluates Qwen models as OpenAI-compatible backends for coding-agent workflows inside OpenCode Harness.

The goal is to compare observable provider behavior: tool-calling stability, JSON fallback discipline, Chinese coding-task quality, repository-context use, latency, step count, and failure taxonomy.

## Scope

- Qwen provider preset through DashScope OpenAI-compatible mode.
- Coding-agent task success rate.
- Native tool-calling and JSON fallback behavior.
- Chinese and bilingual coding tasks.
- Repository context use and cross-file synthesis.
- Provider comparison against DeepSeek, OpenAI, Claude, and local OpenAI-compatible deployments.

## Run

Use the mock provider for lab wiring smoke testing:

```powershell
python -m opencode_harness eval model-labs/qwen/mock-smoke-suite.json --preset mock --max-steps 2
```

Use Qwen through DashScope compatible mode:

```powershell
$env:DASHSCOPE_API_KEY = "..."
python -m opencode_harness eval model-labs/qwen/qwen-coding-agent-suite.json --preset qwen --max-steps 8 --context-chars 8000
```

Run provider comparison:

```powershell
python -m opencode_harness lab-compare `
  model-labs/qwen/qwen-coding-agent-suite.json `
  --presets qwen deepseek openai claude `
  --max-steps 8 `
  --context-chars 8000 `
  --comparison-output model-labs/qwen/reports/provider-comparison.md
```

By default, providers with missing API key environment variables are skipped and listed in the generated comparison.

## Outputs

Eval runs write per-case traces, sessions, `report.json`, `report.md`, and `report.html` under `eval-runs/`.

Use replay to inspect failures:

```powershell
python -m opencode_harness replay eval-runs/<run>/<case>.jsonl --show-content
```

## Clean-Room Boundary

This lab only uses public model APIs, provider documentation, local deployments with authorized weights, and observable runtime behavior. It does not use leaked, proprietary, or unauthorized source code.
