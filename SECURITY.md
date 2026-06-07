# Security Policy

OpenCode Harness executes model-requested tools against local workspaces. Treat model output as untrusted.

## Supported Security Boundaries

- File writes are disabled by default.
- Shell commands are policy-gated.
- Shell command classification blocks compound commands, redirection, network-like commands, and write-like commands by default.
- Network-like install/download commands are blocked by default.
- Tool calls are traced.
- Provider transcripts record request payloads and raw response bodies but do not record API key headers.
- MCP tools must be explicitly configured.
- Optional `approval_mode = "ask"` prompts before blocked writes, blocked shell commands, and MCP-compatible external tool calls.

## Reporting Issues

Please report security issues privately to the project maintainers once a maintainer contact is published. Until then, do not publish exploit details against active users.

## Secrets

Do not commit API keys, provider tokens, private endpoint URLs, or proprietary prompts.

Treat trace files as sensitive if prompts, model responses, local paths, or private provider endpoints contain confidential information.

Use environment variables such as:

- `DEEPSEEK_API_KEY`
- `DASHSCOPE_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

## Clean-Room Security Boundary

This project does not contain, derive from, or depend on leaked or proprietary Claude Code source code. Reports or contributions that require unauthorized source material will not be accepted.
