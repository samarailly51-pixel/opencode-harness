# Product Positioning

OpenCode Harness is a clean-room, model-agnostic AI coding agent harness. It standardizes the execution loop for Claude Code / Codex-class coding agents: task input, planning, tool execution, review, and report generation.

This document explains the product thinking behind the project for AI product manager reviews, AI Agent application discussions, and portfolio presentations.

## Problem

AI coding assistants are easy to demo but hard to evaluate as products.

In many demos, the model receives a prompt, produces code, and the user manually judges the result. That is useful for exploration, but weak for production or serious evaluation because the workflow is opaque:

- The task is not always reproducible.
- The model's tool calls are not always visible.
- File writes and shell commands may not have clear permission boundaries.
- There is no standard failure taxonomy.
- Reports are often missing or manually written.
- Different model providers are hard to compare under the same task surface.

OpenCode Harness addresses this by treating a coding agent as a workflow system, not only a chat interface.

## Why Agent Harness Is Needed

An Agent Harness is the layer between a user task and an AI model. It defines how the agent plans, calls tools, observes results, applies permissions, records traces, and produces reports.

Without a harness, teams often evaluate coding agents through screenshots or anecdotal success cases. With a harness, teams can ask more product-relevant questions:

- Did the agent finish the task or only generate plausible text?
- Which tools did it call, in what order, and with what arguments?
- Did permission policy block unsafe actions?
- Did the agent verify its changes?
- Was the failure caused by the model, the task design, tool output, or eval assertion?
- Can the same task run against another model provider?

This makes the agent workflow measurable and debuggable.

## Target Users

| User | Job To Be Done |
| --- | --- |
| AI Product Manager | Explain the agent workflow, failure modes, product value, and evaluation strategy. |
| AI Agent Engineer | Build and test a provider-neutral coding-agent runtime. |
| Model Evaluation Team | Run the same coding tasks across providers and compare traces/reports. |
| Local Model User | Test local OpenAI-compatible endpoints with a realistic coding-agent workflow. |
| Project Presenter | Demonstrate agent product thinking and engineering execution in one project. |

## Difference From A Normal AI Coding Assistant

| Dimension | Normal AI Coding Assistant | OpenCode Harness |
| --- | --- | --- |
| Primary goal | Help one user write code interactively | Standardize and evaluate coding-agent workflows |
| Output | Chat answer or file edits | Trace, transcript, eval report, comparison report, dashboard |
| Tooling | Usually hidden behind UI | Explicit file/search/patch/shell/MCP tools |
| Permissions | Product-specific behavior | Configurable policy for write, shell, network, MCP calls |
| Evaluation | Manual judgment | JSON eval suites and structured failure taxonomy |
| Provider support | Usually tied to one model/vendor | DeepSeek, Qwen, Claude, OpenAI, local endpoints, mock |
| Product value | Coding assistance | Agent workflow observability and repeatable evaluation |

The project is not trying to replace a polished assistant UI. It focuses on the infrastructure that makes coding agents testable.

## Product Workflow

```text
Task Input -> Planning -> Tool Execution -> Review -> Report
```

| Stage | Product Meaning | Harness Surface |
| --- | --- | --- |
| Task Input | Define the user goal and workspace | CLI task or JSON eval suite |
| Planning | Let the agent decompose work | todo tools and context packing |
| Tool Execution | Let the model act through controlled tools | read/search/patch/shell/MCP tools |
| Review | Verify whether the task is complete | tool outputs, verification command, final marker |
| Report | Turn behavior into evidence | JSONL trace, Markdown/HTML report, dashboard |

## Current Product Evidence

- v0.1.0 release with CI and GitHub Pages.
- Offline mock benchmark for no-key reproducibility.
- DeepSeek-only real API benchmark set.
- DeepSeek failure-mode diagnosis case study.
- Demo video draft and Product Hunt launch package.
- Bilingual documentation for technical and presentation contexts.

## Future Extensions

1. **Before/after reliability fixes**
   Add final-step guard, finish-marker reminder, and repair verification feedback, then re-run the DeepSeek benchmark.

2. **Diagnosis report generator**
   Automatically group failures by failure type, step count, final summary pattern, and tool-loop behavior.

3. **Interactive web dashboard**
   Convert static reports into a web UI for filtering traces, cases, providers, and failure categories.

4. **Provider comparison expansion**
   Run the same suite across Qwen, Claude, OpenAI, and local models when API keys or local endpoints are available.

5. **Dataset and task library**
   Add more coding-agent tasks: documentation edits, bug repair, refactor planning, test generation, dependency inspection, and long-context review.

6. **Team workflow integration**
   Add GitHub issue/PR workflows, scheduled model evals, and artifact uploads for team review.

## Positioning Statement

```text
OpenCode Harness is a clean-room AI coding agent harness for teams who need to run, observe, evaluate, and diagnose coding-agent workflows across model providers.
```

The project should be presented as agent infrastructure and evaluation tooling, not as a proprietary-agent clone or a model leaderboard.
