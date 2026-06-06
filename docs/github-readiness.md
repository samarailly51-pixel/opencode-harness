# GitHub Readiness Checklist

Use this before publishing the repository.

## Required

- [ ] Confirm repository name and description.
- [ ] Review README positioning.
- [ ] Confirm `LICENSE` is correct.
- [ ] Review `CONTRIBUTING.md` clean-room rules.
- [ ] Review `SECURITY.md`.
- [ ] Run the full test suite.
- [ ] Run mock CLI smoke.
- [ ] Run mock eval smoke.
- [ ] Run DeepSeek Lab mock smoke.
- [ ] Confirm no API keys or secrets are present.
- [ ] Confirm `runs/` and `eval-runs/` are ignored.
- [ ] Confirm GitHub Actions CI is enabled after push.
- [ ] Confirm issue and PR templates render on GitHub.
- [ ] Review `docs/release.md`.

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
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness eval model-labs/deepseek/mock-smoke-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness replay runs/latest.jsonl --summary
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
