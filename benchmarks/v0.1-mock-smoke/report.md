# OpenCode Harness v0.1 Mock Smoke Report

OpenCode Harness v0.1.0 was tested with the built-in `mock` provider to verify the end-to-end evaluation surface without requiring API keys.

This report is intentionally conservative: it is a harness/runtime smoke benchmark, not a model intelligence benchmark.

## Result

| Metric | Value |
| --- | ---: |
| Cases | 2 |
| Passed | 2 |
| Failed | 0 |
| Pass rate | 100.0% |
| Total agent steps | 4 |
| Provider transcripts | 4 |
| Failed tool calls | 0 |

## Case Matrix

| Case | Task | Status | Steps | Traceability |
| --- | --- | --- | ---: | --- |
| `inspect-repo` | inspect this repo | PASS | 2 | model response, transcript, tool result, finish |
| `simple-finish` | say hello | PASS | 2 | model response, transcript, tool result, finish |

## What This Demonstrates

- The eval runner can execute a suite and produce per-case results.
- The agent loop records model responses, tool calls, provider transcripts, and finish events.
- Replay tooling can summarize trace timelines.
- The terminal trace viewer can render a readable event timeline.
- HTML trace and dashboard outputs can be generated from the same run artifacts.
- The same workflow can be reused with real provider presets when API keys are available.

## What This Does Not Claim

- It does not rank DeepSeek, Qwen, Claude, OpenAI, or local models.
- It does not claim coding quality superiority.
- It does not use proprietary or leaked source code.
- It does not depend on hidden prompts or private benchmark data.

## Reproduction Command

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
```

## Follow-Up Benchmark Plan

The next public benchmark should run the DeepSeek Lab suite across:

- `deepseek`
- `qwen`
- `openai`
- `claude`
- `local-openai`

The report should publish skipped-provider reasons when API keys or local endpoints are unavailable.
