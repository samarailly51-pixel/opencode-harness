# Eval Report Comparison

| Suite | Provider | Model | Passed | Pass Rate | Failures | Avg Steps | Total Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| deepseek v4 coding-agent smoke | openai-compatible | deepseek-chat | 2/4 | 50.0% | expectation_mismatch=2 | 6.25 | 72.200 |

## Case Matrix

| Case | openai-compatible/deepseek-chat |
| --- | --- |
| chinese-coding-task | PASS (7 steps, 26.20s) |
| patch-proposal-no-write | PASS (8 steps, 19.23s) |
| repo-map-orientation | FAIL:expectation_mismatch (6 steps, 19.44s) |
| tool-calling-stability | FAIL:expectation_mismatch (4 steps, 7.33s) |
