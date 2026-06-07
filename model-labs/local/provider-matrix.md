# Local Provider Matrix

Use this matrix to compare observable behavior across self-hosted OpenAI-compatible deployments.

| Provider | Base URL | Model Name | Native Tools | JSON Fallback | Notes |
| --- | --- | --- | --- | --- | --- |
| Local OpenAI-compatible | `http://localhost:8000` | `local-coder` | TBD | TBD | Generic custom gateway or server. |
| vLLM | `http://localhost:8000` | deployment-specific | TBD | TBD | Useful for throughput and batching experiments. |
| SGLang | `http://localhost:30000` | deployment-specific | TBD | TBD | Useful for structured decoding and serving experiments. |
| Ollama OpenAI Bridge | `http://localhost:11434` | `qwen2.5-coder:7b` | TBD | TBD | Good local smoke target when the OpenAI-compatible endpoint is enabled. |
| DeepSeek Official | `https://api.deepseek.com` | `deepseek-chat` | TBD | TBD | Hosted OpenAI-compatible baseline. |
| Qwen DashScope | `https://dashscope.aliyuncs.com/compatible-mode` | `qwen-plus` | TBD | TBD | Hosted Chinese/coding baseline. |
| OpenAI | `https://api.openai.com` | preset model | TBD | TBD | Hosted general coding-agent baseline. |
| Anthropic Claude | `https://api.anthropic.com` | preset model | TBD | TBD | Hosted Anthropic tool-use baseline. |

## Metrics

- Task pass rate.
- Finished vs stopped runs.
- Model calls per task.
- Tool calls per task.
- Failed tool calls.
- Wall-clock seconds.
- Native tool-call success.
- JSON fallback success.
- Context-window pressure.
- Provider transcript completeness.
- Chinese answer quality and marker adherence.

## Workflow

1. Start the local serving runtime and set the matching API key environment variable to a real token or `dummy`.
2. Run `local-coding-agent-suite.json` directly, or use `opencode_harness lab-compare`.
3. Save `report.json` paths and generated comparison output under `model-labs/local/reports/`.
4. Replay failures with `opencode_harness replay`.
5. Compare reports with `opencode_harness compare` or the generated provider comparison.
