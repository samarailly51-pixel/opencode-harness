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

| Suite | Case | Failure | Finished | Steps | Pattern | Suggested Next Action |
| --- | --- | --- | --- | ---: | --- | --- |
| deepseek v4 long-context suite | repo-wide-module-map | `expectation_mismatch` | True | 5 | Long-context synthesis or marker drift | Reduce context noise or split the task into evidence and synthesis phases. |
| deepseek v4 long-context suite | cross-file-eval-flow | `expectation_mismatch` | True | 7 | Long-context synthesis or marker drift | Reduce context noise or split the task into evidence and synthesis phases. |
| deepseek v4 long-context suite | chinese-long-context-summary | `max_steps` | False | 10 | Tool-loop overrun / missing finalization | Review the final trace events and add stronger finish pressure before raising step budget. |

## Recommended Fixes

1. Separate marker-missing failures from genuinely wrong answers by inspecting the final summary and trace.
2. Keep the eval finish marker visible in the task and after tool observations so models know when to close.
3. Inspect the last two tool calls before increasing `max_steps`; if enough evidence exists, tighten the finish policy.
4. For long-context tasks, split evidence gathering from synthesis and reduce unrelated repository context.
