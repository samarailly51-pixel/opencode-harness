# Real Provider Comparison

This directory contains sanitized benchmark summaries for real provider runs.
Detailed eval traces are written under `eval-runs/` and are intentionally not
committed.

Run:

```powershell
.\scripts\run-real-provider-benchmark.ps1
```

Default providers for the generic runner:

- `deepseek` using `DEEPSEEK_API_KEY`
- `qwen` using `DASHSCOPE_API_KEY`
- `openai` using `OPENAI_API_KEY`
- `claude` using `ANTHROPIC_API_KEY`

DeepSeek-only runner:

```powershell
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet smoke
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet long-context
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet repair
```

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

Latest committed snapshot:

| Field | Value |
| --- | --- |
| Run date | 2026-06-12, Asia/Shanghai |
| Suite | `model-labs/deepseek/deepseek-v4-suite.json` |
| Preset | `deepseek` |
| Provider/model | `openai-compatible` / `deepseek-chat` |
| Result | 2/4 passed, 50.0% pass rate |
| Failures | `expectation_mismatch=2` |
| Average steps | 6.25 |
| Total seconds | 72.200 |

Case matrix:

| Case | Result |
| --- | --- |
| `chinese-coding-task` | PASS |
| `patch-proposal-no-write` | PASS |
| `repo-map-orientation` | FAIL: `expectation_mismatch` |
| `tool-calling-stability` | FAIL: `expectation_mismatch` |

This is a small coding-agent smoke benchmark, not a broad model leaderboard.
The next useful DeepSeek-only work is refreshing the smoke run with the stable
marker-based suite, then adding long-context and repair results.

The public no-key smoke report is still useful for validating harness behavior
without provider credentials:

- [../v0.1-mock-smoke](../v0.1-mock-smoke/README.md)
