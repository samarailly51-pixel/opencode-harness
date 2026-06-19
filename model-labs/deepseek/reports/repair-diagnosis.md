# Failure-Mode Diagnosis

This report summarizes failed eval cases from existing OpenCode Harness `report.json` files.
It is intended for agent-loop debugging, provider comparison, and product-facing case studies.

## Report Snapshot

| Suite | Provider | Model | Passed | Pass Rate | Failed Cases |
| --- | --- | --- | ---: | ---: | ---: |
| deepseek v4 coding-agent repair suite | openai-compatible | deepseek-chat | 0/2 | 0.0% | 2 |

## Failure Type Breakdown

| Failure Type | Count |
| --- | ---: |
| `expectation_mismatch` | 2 |

## Case Diagnostics

| Suite | Case | Failure | Finished | Steps | Pattern | Suggested Next Action |
| --- | --- | --- | --- | ---: | --- | --- |
| deepseek v4 coding-agent repair suite | repair-calculator | `expectation_mismatch` | True | 5 | Repair finalization gap | Require test rerun evidence and a final pass marker in the finish summary. |
| deepseek v4 coding-agent repair suite | repair-text-utils | `expectation_mismatch` | True | 8 | Repair finalization gap | Require test rerun evidence and a final pass marker in the finish summary. |

## Recommended Fixes

1. Separate marker-missing failures from genuinely wrong answers by inspecting the final summary and trace.
2. Keep the eval finish marker visible in the task and after tool observations so models know when to close.
3. For repair tasks, prefer copied fixture workspaces, explicit test commands, and a required pass marker.
