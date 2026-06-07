# Qwen Provider Matrix

Use this matrix to compare observable behavior across Qwen-compatible providers and baseline providers.

| Provider | Base URL | Model Name | Native Tools | JSON Fallback | Notes |
| --- | --- | --- | --- | --- | --- |
| DashScope Qwen | `https://dashscope.aliyuncs.com/compatible-mode` | `qwen-plus` | TBD | TBD | Baseline Qwen preset. |
| Qwen Coder | provider-specific | provider-specific | TBD | TBD | Coding-specialized track. |
| Local vLLM | local OpenAI-compatible URL | provider-specific | TBD | TBD | Requires authorized weights/deployment. |
| Local SGLang | local OpenAI-compatible URL | provider-specific | TBD | TBD | Useful for throughput and long-context tests. |
| DeepSeek Official | `https://api.deepseek.com` | `deepseek-chat` | TBD | TBD | Cross-provider baseline. |
| OpenAI | `https://api.openai.com` | preset model | TBD | TBD | General coding-agent baseline. |

## Metrics

- Task pass rate.
- Finished vs stopped runs.
- Model calls per task.
- Tool calls per task.
- Failed tool calls.
- Wall-clock seconds.
- Native tool-call success.
- JSON fallback success.
- Chinese answer quality and marker adherence.
- Repository context synthesis quality.

## Workflow

1. Run `qwen-coding-agent-suite.json` directly, or use `opencode_harness lab-compare`.
2. Save `report.json` paths and generated comparison output under `model-labs/qwen/reports/`.
3. Replay failures with `opencode_harness replay`.
4. Compare reports with `opencode_harness compare` or the generated provider comparison.
5. Record observations in Notes.
