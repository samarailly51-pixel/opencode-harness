# Failure-Mode Diagnosis

This report summarizes failed eval cases from existing OpenCode Harness `report.json` files.
It is intended for agent-loop debugging, provider comparison, and product-facing case studies.

## Report Snapshot

| Suite | Provider | Model | Passed | Pass Rate | Failed Cases |
| --- | --- | --- | ---: | ---: | ---: |
| deepseek v4 long-context suite | openai-compatible | deepseek-chat | 1/4 | 25.0% | 3 |

## Failure Type Breakdown

| Failure Type | Count |
| --- | ---: |
| `expectation_mismatch` | 2 |
| `max_steps` | 1 |

## Case Diagnostics

| Suite | Case | Failure | Finished | Steps | Pattern | Trace Signals | Suggested Next Action |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| deepseek v4 long-context suite | repo-wide-module-map | `expectation_mismatch` | True | 5 | Long-context synthesis or marker drift | events=12, model_calls=5, tool_calls=4, last_tools=read_file > read_file > read_file, repeated_tail=read_file | Review repeated `read_file` calls and add a loop-break or synthesis step. |
| deepseek v4 long-context suite | cross-file-eval-flow | `expectation_mismatch` | True | 7 | Long-context synthesis or marker drift | events=16, model_calls=7, tool_calls=6, last_tools=read_file > read_file > read_file, repeated_tail=read_file | Review repeated `read_file` calls and add a loop-break or synthesis step. |
| deepseek v4 long-context suite | chinese-long-context-summary | `max_steps` | False | 10 | Tool-loop overrun / missing finalization | events=23, model_calls=10, tool_calls=10, last_tools=read_file > read_file > read_file, repeated_tail=read_file, no_finish_event | Review repeated `read_file` calls and add a loop-break or synthesis step. |

## Recommended Fixes

1. Separate marker-missing failures from genuinely wrong answers by inspecting the final summary and trace.
2. Keep the eval finish marker visible in the task and after tool observations so models know when to close.
3. Inspect the last two tool calls before increasing `max_steps`; if enough evidence exists, tighten the finish policy.
4. For long-context tasks, split evidence gathering from synthesis and reduce unrelated repository context.
5. Add loop-break rules for repeated tool calls when the last trace events show the same tool pattern.
