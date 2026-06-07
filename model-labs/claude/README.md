# Claude Lab

Claude Lab evaluates Claude models through the Anthropic Messages API inside OpenCode Harness.

The goal is not to clone Claude Code internals. The goal is to measure Claude provider behavior in the same clean-room harness used for DeepSeek, Qwen, OpenAI, and local models.

## Scope

- Anthropic native `tool_use` behavior.
- JSON fallback behavior when native tools are unavailable.
- Repository-context synthesis.
- Coding-agent repair and edit workflows.
- Chinese and bilingual task quality.
- Provider comparison against DeepSeek, Qwen, OpenAI, and local OpenAI-compatible deployments.

## Run

Use the mock provider for lab wiring smoke testing:

```powershell
python -m opencode_harness eval model-labs/claude/mock-smoke-suite.json --preset mock --max-steps 2
```

Use Claude through the Anthropic API:

```powershell
$env:ANTHROPIC_API_KEY = "..."
python -m opencode_harness eval model-labs/claude/claude-coding-agent-suite.json --preset claude --max-steps 8 --context-chars 8000
```

Run provider comparison:

```powershell
python -m opencode_harness lab-compare `
  model-labs/claude/claude-coding-agent-suite.json `
  --presets claude deepseek qwen openai `
  --max-steps 8 `
  --context-chars 8000 `
  --comparison-output model-labs/claude/reports/provider-comparison.md
```

By default, providers with missing API key environment variables are skipped and listed in the generated comparison.

## Outputs

Eval runs write per-case traces, sessions, `report.json`, `report.md`, and `report.html` under `eval-runs/`.

Use replay to inspect failures:

```powershell
python -m opencode_harness replay eval-runs/<run>/<case>.jsonl --show-content
```

## Clean-Room Boundary

This lab only uses public Anthropic APIs, public provider documentation, and observable runtime behavior. It does not contain, derive from, or depend on Claude Code source code.
