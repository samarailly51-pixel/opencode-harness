# Claude Provider Matrix

Use this matrix to compare observable Claude behavior against other coding-agent providers.

| Provider | Base URL | Model Name | Native Tools | JSON Fallback | Notes |
| --- | --- | --- | --- | --- | --- |
| Anthropic Claude | `https://api.anthropic.com` | preset model | TBD | TBD | Baseline Claude preset. |
| DeepSeek Official | `https://api.deepseek.com` | `deepseek-chat` | TBD | TBD | Cross-provider baseline. |
| DashScope Qwen | `https://dashscope.aliyuncs.com/compatible-mode` | `qwen-plus` | TBD | TBD | Chinese/coding baseline. |
| OpenAI | `https://api.openai.com` | preset model | TBD | TBD | General coding-agent baseline. |
| Local OpenAI-compatible | local URL | provider-specific | TBD | TBD | Useful for controlled local deployments. |

## Metrics

- Task pass rate.
- Finished vs stopped runs.
- Anthropic native `tool_use` success.
- JSON fallback success.
- Tool calls per task.
- Failed tool calls.
- Wall-clock seconds.
- Repair-readiness explanation quality.
- Chinese answer quality and marker adherence.
- Repository context synthesis quality.

## Workflow

1. Run `claude-coding-agent-suite.json` directly, or use `opencode_harness lab-compare`.
2. Save `report.json` paths and generated comparison output under `model-labs/claude/reports/`.
3. Replay failures with `opencode_harness replay`.
4. Compare reports with `opencode_harness compare` or the generated provider comparison.
5. Record observations in Notes.
