# Eval Report Comparison

| Suite | Provider | Model | Passed | Pass Rate | Failures | Avg Steps | Total Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| deepseek v4 coding-agent repair suite | openai-compatible | deepseek-chat | 0/2 | 0.0% | expectation_mismatch=2 | 6.50 | 21.032 |

## Case Matrix

| Case | openai-compatible/deepseek-chat |
| --- | --- |
| repair-calculator | FAIL:expectation_mismatch (5 steps, 8.62s) |
| repair-text-utils | FAIL:expectation_mismatch (8 steps, 12.41s) |
