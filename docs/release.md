# Release Guide

This guide is for publishing OpenCode Harness.

## Pre-Release Checks

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness eval model-labs/deepseek/mock-smoke-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness replay runs/latest.jsonl --summary
```

Review:

- `README.md`
- `ROADMAP.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/github-readiness.md`
- `model-labs/deepseek/README.md`

Check:

```powershell
git status --short
git log -1 --oneline
```

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
Initial clean-room OpenCode Harness release.

Highlights:
- Claude Code-class coding-agent runtime.
- DeepSeek/Qwen/OpenAI/Claude provider support.
- Native OpenAI-compatible and Anthropic tool use.
- JSON fallback tool protocol.
- Permission-gated file, shell, patch, repo map, context, todo, and MCP tools.
- JSONL traces, session state, replay, and JSON/Markdown eval reports.
- DeepSeek Lab for provider and behavior evaluation.
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
