# Eval Report Comparison

| Suite | Provider | Model | Passed | Pass Rate | Failures | Avg Steps | Total Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| deepseek v4 coding-agent smoke | openai-compatible | deepseek-chat | 1/4 | 25.0% | expectation_mismatch=3 | 5.50 | 67.418 |

## Case Matrix

| Case | openai-compatible/deepseek-chat |
| --- | --- |
| chinese-coding-task | FAIL:expectation_mismatch (5 steps, 18.96s) |
| patch-proposal-no-write | PASS (6 steps, 21.68s) |
| repo-map-orientation | FAIL:expectation_mismatch (7 steps, 19.11s) |
| tool-calling-stability | FAIL:expectation_mismatch (4 steps, 7.66s) |
