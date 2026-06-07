# DeepSeek Provider Matrix

Use this matrix to compare observable behavior across providers.

| Provider | Base URL | Model Name | Native Tools | JSON Fallback | Notes |
| --- | --- | --- | --- | --- | --- |
| DeepSeek Official | `https://api.deepseek.com` | `deepseek-chat` | TBD | TBD | Baseline official API. |
| DeepSeek Official Reasoner | `https://api.deepseek.com` | `deepseek-reasoner` | TBD | TBD | Reasoning behavior track. |
| Local vLLM | local OpenAI-compatible URL | provider-specific | TBD | TBD | Requires authorized weights/deployment. |
| Local SGLang | local OpenAI-compatible URL | provider-specific | TBD | TBD | Useful for throughput and long-context tests. |
| OpenRouter | provider URL | provider-specific | TBD | TBD | Check template/tool differences. |
| SiliconFlow | provider URL | provider-specific | TBD | TBD | Check latency, truncation, and cost. |

## Metrics

- Task pass rate.
- Finished vs stopped runs.
- Model calls per task.
- Tool calls per task.
- Failed tool calls.
- Wall-clock seconds.
- Native tool-call success.
- JSON fallback success.
- Final answer language and format adherence.
- Context truncation symptoms.

## Workflow

1. Create or update a config for the provider.
2. Run `deepseek-v4-suite.json` directly, or use `opencode_harness lab-compare`.
3. Save `report.json` paths and generated comparison output under `model-labs/deepseek/reports/`.
4. Replay failures with `opencode_harness replay`.
5. Compare reports with `opencode_harness compare` or the generated provider comparison.
6. Record observations in Notes.
