# GitHub Readiness Checklist

Use this before publishing the repository.

## Required

- [x] Confirm repository name and description.
- [x] Review README positioning.
- [x] Confirm `LICENSE` is correct.
- [x] Review `CONTRIBUTING.md` clean-room rules.
- [x] Review `SECURITY.md`.
- [x] Run the full test suite.
- [x] Run mock CLI smoke.
- [x] Run mock eval smoke.
- [x] Run DeepSeek Lab mock smoke.
- [x] Confirm no API keys or secrets are present.
- [x] Confirm `runs/` and `eval-runs/` are ignored.
- [x] Confirm GitHub Actions CI passes after push.
- [x] Confirm issue and PR templates render on GitHub.
- [x] Review `docs/release.md`.

## Recommended

- [x] Add GitHub Actions CI.
- [x] Add issue templates.
- [x] Add pull request template.
- [ ] Add a first release tag.
- [x] Add example provider configs.
- [x] Add a project roadmap.

## Local Verification Commands

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m opencode_harness version
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness eval model-labs/deepseek/mock-smoke-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness replay runs/latest.jsonl --summary
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

## Positioning

Recommended short description:

```text
A clean-room, model-agnostic harness for Claude Code-class coding agents, with DeepSeek/Qwen/Claude/OpenAI backends, MCP tools, trace replay, and evals.
```

Recommended disclaimer:

```text
This project is a clean-room implementation. It does not contain, derive from, or depend on leaked or proprietary Claude Code source code.
```
