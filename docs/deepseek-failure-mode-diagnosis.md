# DeepSeek Failure-Mode Diagnosis

Last updated: 2026-06-19, Asia/Shanghai.

This diagnosis turns the first DeepSeek-only benchmark set into product evidence
for OpenCode Harness. The goal is not to rank DeepSeek broadly. The goal is to
show that the harness can expose concrete coding-agent failure modes with
repeatable suites, traces, reports, and comparison summaries.

## Benchmark Snapshot

Provider/model:

```text
openai-compatible / deepseek-chat
```

Runner:

```powershell
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet all
```

Published summaries:

- [Smoke comparison](../model-labs/deepseek/reports/provider-comparison.md)
- [Long-context comparison](../model-labs/deepseek/reports/long-context-comparison.md)
- [Repair comparison](../model-labs/deepseek/reports/repair-comparison.md)
- [Real provider comparison package](../benchmarks/real-provider-comparison/README.md)

## Results

| Suite | Passed | Pass Rate | Failure Types |
| --- | ---: | ---: | --- |
| Smoke | 1/4 | 25.0% | `expectation_mismatch=3` |
| Long context | 1/4 | 25.0% | `expectation_mismatch=2`, `max_steps=1` |
| Repair | 0/2 | 0.0% | `expectation_mismatch=2` |

## What Failed

| Failure Mode | Evidence | Interpretation |
| --- | --- | --- |
| Marker-following drift | Smoke Chinese task failed after missing `ZH_MODEL_SUMMARY`; long-context Chinese task hit `max_steps` before `LONG_CONTEXT_ZH`. | The model can keep inspecting files but does not reliably close with the required completion marker. |
| Tool-loop overrun | Several cases summarize an intention to inspect more files instead of finishing. | The agent loop needs stronger finish pressure and possibly a stricter step budget policy. |
| Long-context synthesis gap | Only `security-and-permissions-context` passed in the long-context suite. | The model can produce a deep focused safety explanation, but broad repository synthesis is less stable. |
| Repair finalization gap | Both repair cases failed `expectation_mismatch` despite touching copied fixture workspaces. | The repair loop needs better test-result feedback, patch verification, and finish-marker enforcement. |

## What Passed

- `patch-proposal-no-write` passed in the smoke suite.
- `security-and-permissions-context` passed in the long-context suite.

These passes matter because they show the model can use the harness for focused
inspection and safety-oriented synthesis. The failures are concentrated around
closing behavior, marker adherence, and repair verification rather than basic
provider connectivity.

## Harness Value

This benchmark set proves four things about the harness:

- It runs real provider calls through the same agent loop and tool layer.
- It records failure types instead of collapsing all failures into a generic score.
- It separates public summaries from sensitive raw traces under `eval-runs/`.
- It gives a concrete next-work queue for improving agent reliability.

## Automated Diagnosis Command

The harness now includes a report-level diagnosis command:

```powershell
python -m opencode_harness diagnose `
  eval-runs/path-to-run/report.json `
  --output eval-runs/deepseek-diagnosis.md
```

The command reads saved eval reports and produces a Markdown diagnosis with:

- report snapshot
- failure type breakdown
- case-level inferred patterns
- suggested next actions
- recommended reliability fixes

## Reliability Fixes

Implemented:

1. Add a finish-marker reminder after each tool result when an eval has `expect_contains`.
2. Add a final-step guard that asks the model to stop inspecting and answer when only one step remains.
3. Add a diagnosis report generator that groups failures by case, failure type, step count, and final summary pattern.

Next:

1. Improve repair suite feedback by surfacing verification command output more explicitly.
2. Re-run the DeepSeek-only suite after each loop or prompt change.
3. Compare before/after pass rates and failure modes across the same suites.

## Public Positioning

Use this wording:

```text
OpenCode Harness published a DeepSeek-only diagnostic benchmark set. The results
are intentionally not polished into a leaderboard: smoke 1/4, long-context 1/4,
and repair 0/2. The value is that the harness exposes concrete coding-agent
failure modes such as marker drift, tool-loop overrun, long-context synthesis
gaps, and repair finalization gaps.
```

Avoid this wording:

```text
DeepSeek is bad at coding agents.
OpenCode Harness is better than Claude Code.
This is a definitive DeepSeek V4 ranking.
```
