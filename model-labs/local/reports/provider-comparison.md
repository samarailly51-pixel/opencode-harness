# Eval Report Comparison

| Suite | Provider | Model | Passed | Pass Rate | Failures | Avg Steps | Total Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| local lab mock smoke | mock | mock-coder | 1/1 | 100.0% | - | 2.00 | 0.164 |

## Case Matrix

| Case | mock/mock-coder |
| --- | --- |
| lab-loads | PASS (2 steps, 0.16s) |

## Skipped Providers

| Preset | Reason |
| --- | --- |
| local-openai | missing LOCAL_MODEL_API_KEY |
| vllm | missing VLLM_API_KEY |
| sglang | missing SGLANG_API_KEY |
| ollama | missing OLLAMA_API_KEY |
