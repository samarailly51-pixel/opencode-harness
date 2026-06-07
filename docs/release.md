# Release Guide

This guide is for publishing OpenCode Harness.

## Pre-Release Checks

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m opencode_harness version
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness eval model-labs/deepseek/mock-smoke-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness replay runs/latest.jsonl --summary
python -m opencode_harness dashboard eval-runs --output eval-runs/dashboard.html
```

Review:

- `README.md`
- `ROADMAP.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/github-readiness.md`
- `docs/provider-benchmarks.md`
- `CHANGELOG.md`
- `examples/release-demo/README.md`
- `model-labs/deepseek/README.md`

Check:

```powershell
git status --short
git log -1 --oneline
python -m pip wheel . --no-deps -w dist-check
```

Remove `dist-check/` after local wheel verification.

## GitHub Release

1. Push the repository.
2. Confirm GitHub Actions passes.
3. Create a tag:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

4. Create a GitHub release from the tag.

Suggested release title:

```text
OpenCode Harness v0.1.0
```

Repository:

```text
https://github.com/samarailly51-pixel/opencode-harness
```

Suggested release notes:

```text
OpenCode Harness v0.1.0

Initial clean-room release for model-agnostic coding-agent evaluation.

Highlights:
- Claude Code-class coding-agent runtime.
- DeepSeek/Qwen/OpenAI/Claude/local provider support.
- Native OpenAI-compatible and Anthropic tool use.
- JSON fallback tool protocol.
- Permission-gated file, shell, patch, repo map, context, todo, and MCP tools.
- MCP resources, prompts, diagnostics, per-server approvals, and namespace collision handling.
- JSONL traces, provider transcripts, session state, replay, TUI/HTML viewers, and eval dashboard.
- DeepSeek, Qwen, Claude, OpenAI, and Local Model Labs.
- GitHub Actions CI, release package build workflow, and model-eval workflow example.
```

## PyPI

PyPI publishing is optional. Before publishing:

- Confirm the package name is available.
- Decide whether `opencode-harness` should be reserved now.
- Add build/publish automation.
- Verify install from a local wheel.

Local build command, once build tooling is installed:

```powershell
python -m build
```

Do not publish credentials or API keys.
