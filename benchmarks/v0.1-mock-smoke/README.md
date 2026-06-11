# v0.1 Mock Smoke Benchmark

This benchmark is the public, reproducible demo report for OpenCode Harness v0.1.0.

It validates the harness surface itself:

- eval suite execution
- provider preset loading
- agent loop stepping
- tool-call tracing
- provider transcript capture
- report generation
- terminal trace viewer
- HTML trace viewer
- dashboard generation

It does **not** claim model-quality superiority. The provider is `mock`, which exists so anyone can verify the runtime without API keys.

## Summary

| Field | Value |
| --- | --- |
| Date | 2026-06-11 |
| Suite | `examples/mock-suite.json` |
| Provider preset | `mock` |
| Model provider | `mock` |
| Model name | `mock-coder` |
| Cases | 2 |
| Passed | 2 |
| Pass rate | 100.0% |
| Total steps | 4 |
| Failed tools | 0 |
| Provider transcripts | 4 |

## Results

| Case | Status | Finished | Steps | Failure Type | Expected Signal |
| --- | --- | --- | ---: | --- | --- |
| `inspect-repo` | PASS | true | 2 | - | `Mock run completed` |
| `simple-finish` | PASS | true | 2 | - | `Mock run completed` |

## Reproduce

From the repository root:

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
```

Generate trace and dashboard surfaces:

```powershell
$trace = Get-ChildItem eval-runs -Recurse -Filter inspect-repo.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
python -m opencode_harness replay $trace.FullName
python -m opencode_harness tui $trace.FullName --width 88
python -m opencode_harness trace-html $trace.FullName --output eval-runs/latest-trace.html
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

Or generate all recording/demo artifacts:

```powershell
.\scripts\recording-demo.ps1
```

## Evidence

The mock run emits the same artifact classes as real provider runs:

- `report.json`
- `report.md`
- `report.html`
- per-case `*.jsonl` traces
- per-case session files
- terminal replay output
- terminal trace viewer output
- standalone HTML trace viewer
- standalone dashboard HTML

Each case includes model response events, provider transcript events, tool result events, and a final finish event.

## Next Provider Benchmark

Use the same suite shape with real provider presets:

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-suite.json `
  --presets deepseek qwen openai claude `
  --comparison-output model-labs/deepseek/reports/provider-comparison.md
```

Real-provider reports should include:

- pass rate
- failure types
- average steps
- total seconds
- per-case matrix
- skipped providers with missing-key reasons
- trace and transcript availability notes

## Files

- Machine-readable summary: [report.json](report.json)
- Product-facing report: [report.md](report.md)
- Recording workflow: [../../docs/video-production-kit.md](../../docs/video-production-kit.md)
- Provider benchmark guide: [../../docs/provider-benchmarks.md](../../docs/provider-benchmarks.md)
