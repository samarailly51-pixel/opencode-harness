# Real Provider Comparison

This directory is reserved for real provider benchmark outputs.

Run:

```powershell
.\scripts\run-real-provider-benchmark.ps1
```

Default providers:

- `deepseek` using `DEEPSEEK_API_KEY`
- `qwen` using `DASHSCOPE_API_KEY`
- `openai` using `OPENAI_API_KEY`
- `claude` using `ANTHROPIC_API_KEY`

Default suite:

```text
model-labs/deepseek/deepseek-v4-suite.json
```

Outputs:

- `provider-comparison.md`
- `provider-comparison.json`
- `eval-runs/real-provider-benchmark/**`

If API keys are missing, the comparison report records skipped providers instead of pretending that a benchmark ran.

## Current Status

No real provider API keys are configured in the current local environment, so no real provider model run has been executed yet.

Use the public no-key smoke report until real provider results are available:

- [../v0.1-mock-smoke](../v0.1-mock-smoke/README.md)
