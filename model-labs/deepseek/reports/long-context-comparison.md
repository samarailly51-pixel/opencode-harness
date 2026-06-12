# Eval Report Comparison

| Suite | Provider | Model | Passed | Pass Rate | Failures | Avg Steps | Total Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| deepseek v4 long-context suite | openai-compatible | deepseek-chat | 1/4 | 25.0% | expectation_mismatch=2, max_steps=1 | 7.00 | 65.886 |

## Case Matrix

| Case | openai-compatible/deepseek-chat |
| --- | --- |
| chinese-long-context-summary | FAIL:max_steps (10 steps, 18.29s) |
| cross-file-eval-flow | FAIL:expectation_mismatch (7 steps, 11.54s) |
| repo-wide-module-map | FAIL:expectation_mismatch (5 steps, 10.95s) |
| security-and-permissions-context | PASS (6 steps, 25.11s) |
