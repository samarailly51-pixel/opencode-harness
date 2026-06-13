# Demo Workflow

This example shows how OpenCode Harness turns a coding-agent task into a structured workflow: Task Input -> Planning -> Tool Execution -> Review -> Report.

## Scenario

A developer wants an AI coding agent to inspect a repository and suggest one small documentation improvement. The agent should not edit files in this demo; it should only inspect, reason, and produce a patch idea.

## 1. Task Input

Task:

```text
Inspect README.md and propose one small documentation improvement.
Do not edit files; finish with the proposed patch idea.
```

Equivalent eval case shape:

```json
{
  "id": "patch-proposal-no-write",
  "task": "Inspect README.md and propose one small documentation improvement. Do not edit files; finish with the proposed patch idea.",
  "workspace": ".",
  "expect_contains": "README"
}
```

Run with mock provider:

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2
```

Run with DeepSeek provider:

```powershell
$env:DEEPSEEK_API_KEY = "..."
python -m opencode_harness eval model-labs/deepseek/deepseek-v4-suite.json --preset deepseek --max-steps 8
```

## 2. Planning

The agent should create or internally follow a short plan:

```text
1. Read README.md.
2. Identify one confusing or missing section.
3. Propose a minimal documentation patch.
4. Finish without writing files.
```

In OpenCode Harness, planning can be represented through todo tools or through the agent's internal reasoning and final summary. The important product point is that planning becomes part of the traceable workflow rather than an invisible step.

## 3. Tool Execution

Expected tool calls:

```text
read_file README.md
search_text "Quick Start" or "DeepSeek"
finish with proposed patch idea
```

Depending on the provider, the tool call can be returned as native tool calls or as the provider-neutral JSON tool protocol. The harness normalizes the behavior into tool execution events and records them in JSONL trace files.

## 4. Review

The agent reviews whether the task is complete:

| Review Question | Expected Answer |
| --- | --- |
| Did it inspect the relevant file? | Yes, `README.md` was read. |
| Did it avoid file writes? | Yes, no write/patch tool should be used. |
| Did it propose a concrete improvement? | Yes, the final answer should include a patch idea. |
| Did it satisfy the eval assertion? | The summary should contain `README`. |

If the agent keeps reading files without finishing, the harness will eventually hit `max_steps`. If it finishes but misses the expected output, the report records `expectation_mismatch`.

## 5. Output Report

Each eval run writes artifacts under `eval-runs/`:

```text
report.json
report.md
report.html
latest.jsonl
<case-id>.jsonl
<case-id>.session.json
```

The report includes:

- total cases
- pass/fail count
- failure type
- step count
- runtime
- final summary
- trace path
- session path

Example comparison output:

```text
| Suite | Provider | Model | Passed | Pass Rate | Failures | Avg Steps | Total Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| deepseek v4 coding-agent smoke | openai-compatible | deepseek-chat | 1/4 | 25.0% | expectation_mismatch=3 | 5.50 | 67.418 |
```

## 6. Product Interpretation

This demo is intentionally simple. Its purpose is to show the harness workflow:

- The user task becomes a repeatable eval case.
- The agent's actions are executed through controlled tools.
- The trace records what happened.
- The report explains whether the case passed and why it failed.
- The same task can later run against another provider or agent loop.

For AI product work, this turns "the model gave me an answer" into a measurable product workflow.
