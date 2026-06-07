# OpenAI Provider Matrix

Use this matrix to compare observable OpenAI behavior against other coding-agent providers.

| Provider | Base URL | Model Name | Native Tools | JSON Fallback | Notes |
| --- | --- | --- | --- | --- | --- |
| OpenAI | `https://api.openai.com` | preset model | TBD | TBD | Baseline OpenAI preset. |
| DeepSeek Official | `https://api.deepseek.com` | `deepseek-chat` | TBD | TBD | OpenAI-compatible cross-provider baseline. |
| DashScope Qwen | `https://dashscope.aliyuncs.com/compatible-mode` | `qwen-plus` | TBD | TBD | Chinese/coding baseline. |
| Anthropic Claude | `https://api.anthropic.com` | preset model | TBD | TBD | Anthropic tool-use baseline. |
| Local OpenAI-compatible | local URL | provider-specific | TBD | TBD | vLLM/SGLang/Ollama-compatible deployments. |

## Metrics

- Task pass rate.
- Finished vs stopped runs.
- Native tool-call success.
- JSON fallback success.
- Tool calls per task.
- Failed tool calls.
- Wall-clock seconds.
- Provider transcript completeness.
- Chinese answer quality and marker adherence.
- Repository context synthesis quality.

## Workflow

1. Run `openai-coding-agent-suite.json` directly, or use `opencode_harness lab-compare`.
2. Save `report.json` paths and generated comparison output under `model-labs/openai/reports/`.
3. Replay failures with `opencode_harness replay`.
4. Compare reports with `opencode_harness compare` or the generated provider comparison.
5. Record observations in Notes.
