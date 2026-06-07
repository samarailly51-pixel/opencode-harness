# Release Demo

This directory documents the reproducible v0.1 demo flow.

The commands generate local artifacts under `eval-runs/`, which is intentionally ignored by git.

## Commands

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness version
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
$trace = Get-ChildItem eval-runs -Recurse -Filter inspect-repo.jsonl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
python -m opencode_harness tui $trace.FullName --width 80
python -m opencode_harness trace-html $trace.FullName --output eval-runs/latest-trace.html
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

## Expected Artifacts

- `eval-runs/**/report.json`
- `eval-runs/**/report.md`
- `eval-runs/**/report.html`
- `eval-runs/**/*.jsonl`
- `eval-runs/latest-trace.html`
- `eval-runs/dashboard.html`
