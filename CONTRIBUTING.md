# Contributing

Thanks for helping build OpenCode Harness.

This project is a clean-room implementation of a Claude Code-class coding-agent harness. Contributions must be based on original work, public documentation, public APIs, observable behavior, or legally licensed open-source code.

## Clean-Room Rules

Do not contribute code, prompts, tests, docs, or implementation details copied or derived from:

- leaked source code
- proprietary source code
- reverse-engineered closed-source binaries
- private internal documents
- code you do not have the right to license

When in doubt, describe the source of an idea in the pull request.

## Development

Run tests:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
```

Run a smoke eval:

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2
```

Run DeepSeek Lab smoke:

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval model-labs/deepseek/mock-smoke-suite.json --preset mock --max-steps 2
```

## Pull Request Checklist

- Keep changes focused.
- Add or update tests for behavior changes.
- Update README or docs for user-facing changes.
- Do not commit `runs/`, `eval-runs/`, secrets, or provider API keys.
- Do not weaken permission checks without a clear reason and test coverage.
