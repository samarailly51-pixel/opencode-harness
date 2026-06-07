# OpenAI Lab

OpenAI Lab evaluates OpenAI models as OpenAI-compatible coding-agent backends inside OpenCode Harness.

The goal is to keep a strong general-purpose baseline for comparing DeepSeek, Qwen, Claude, and local OpenAI-compatible deployments on the same agent loop, tools, permissions, traces, and eval reports.

## Scope

- OpenAI-compatible native tool calls.
- JSON fallback behavior.
- Repository-context synthesis.
- Coding-agent repair readiness.
- Provider transcript auditability.
- Chinese and bilingual coding tasks.
- Provider comparison against DeepSeek, Qwen, Claude, and local deployments.

## Run

Use the mock provider for lab wiring smoke testing:

```powershell
python -m opencode_harness eval model-labs/openai/mock-smoke-suite.json --preset mock --max-steps 2
```

Use OpenAI through the OpenAI-compatible adapter:

```powershell
$env:OPENAI_API_KEY = "..."
python -m opencode_harness eval model-labs/openai/openai-coding-agent-suite.json --preset openai --max-steps 8 --context-chars 8000
```

Run provider comparison:

```powershell
python -m opencode_harness lab-compare `
  model-labs/openai/openai-coding-agent-suite.json `
  --presets openai deepseek qwen claude `
  --max-steps 8 `
  --context-chars 8000 `
  --comparison-output model-labs/openai/reports/provider-comparison.md
```

By default, providers with missing API key environment variables are skipped and listed in the generated comparison.

## Outputs

Eval runs write per-case traces, sessions, `report.json`, `report.md`, and `report.html` under `eval-runs/`.

Use replay to inspect failures:

```powershell
python -m opencode_harness replay eval-runs/<run>/<case>.jsonl --show-content
```

## Clean-Room Boundary

This lab only uses public OpenAI APIs, public provider documentation, and observable runtime behavior. It does not use leaked, proprietary, or unauthorized source code.
