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

Latest committed DeepSeek-only snapshot:

| Field | Value |
| --- | --- |
| Run date | 2026-06-12, Asia/Shanghai |
| Preset | `deepseek` |
| Provider/model | `openai-compatible` / `deepseek-chat` |
| Smoke result | 1/4 passed, 25.0% pass rate |
| Long-context result | 1/4 passed, 25.0% pass rate |
| Repair result | 0/2 passed, 0.0% pass rate |

Smoke case matrix:

| Case | Result |
| --- | --- |
| `chinese-coding-task` | FAIL: `expectation_mismatch` |
| `patch-proposal-no-write` | PASS |
| `repo-map-orientation` | FAIL: `expectation_mismatch` |
| `tool-calling-stability` | FAIL: `expectation_mismatch` |

Long-context case matrix:

| Case | Result |
| --- | --- |
| `repo-wide-module-map` | FAIL: `expectation_mismatch` |
| `cross-file-eval-flow` | FAIL: `expectation_mismatch` |
| `security-and-permissions-context` | PASS |
| `chinese-long-context-summary` | FAIL: `max_steps` |

Repair case matrix:

| Case | Result |
| --- | --- |
| `repair-calculator` | FAIL: `expectation_mismatch` |
| `repair-text-utils` | FAIL: `expectation_mismatch` |

These are small coding-agent diagnostic benchmarks, not a broad model
leaderboard. They are useful because they expose concrete failure modes in
marker following, tool-loop completion, long-context synthesis, and repair task
finalization.

The public no-key smoke report is still useful for validating harness behavior
without provider credentials:

- [../v0.1-mock-smoke](../v0.1-mock-smoke/README.md)
