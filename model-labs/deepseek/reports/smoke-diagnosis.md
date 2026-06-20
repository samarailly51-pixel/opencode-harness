# Failure-Mode Diagnosis

This report summarizes failed eval cases from existing OpenCode Harness `report.json` files.
It is intended for agent-loop debugging, provider comparison, and product-facing case studies.

## Report Snapshot

| Suite | Provider | Model | Passed | Pass Rate | Failed Cases |
| --- | --- | --- | ---: | ---: | ---: |
| deepseek v4 coding-agent smoke | openai-compatible | deepseek-chat | 1/4 | 25.0% | 3 |

## Failure Type Breakdown

| Failure Type | Count |
| --- | ---: |
| `expectation_mismatch` | 3 |

## Case Diagnostics

| Suite | Case | Failure | Finished | Steps | Pattern | Trace Signals | Suggested Next Action |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| deepseek v4 coding-agent smoke | repo-map-orientation | `expectation_mismatch` | True | 7 | Finish-marker drift | events=16, model_calls=7, tool_calls=6, last_tools=read_file > read_file > read_file, repeated_tail=read_file | Review repeated `read_file` calls and add a loop-break or synthesis step. |
| deepseek v4 coding-agent smoke | tool-calling-stability | `expectation_mismatch` | True | 4 | Finish-marker drift | events=11, model_calls=4, tool_calls=4, last_tools=read_file > todo_set > finish | Check whether the summary missed only the marker or missed the task requirement. |
| deepseek v4 coding-agent smoke | chinese-coding-task | `expectation_mismatch` | True | 5 | Finish-marker drift | events=12, model_calls=5, tool_calls=4, last_tools=read_file > read_file > read_file, repeated_tail=read_file | Review repeated `read_file` calls and add a loop-break or synthesis step. |

## Recommended Fixes

1. Separate marker-missing failures from genuinely wrong answers by inspecting the final summary and trace.
2. Keep the eval finish marker visible in the task and after tool observations so models know when to close.
3. Add loop-break rules for repeated tool calls when the last trace events show the same tool pattern.
