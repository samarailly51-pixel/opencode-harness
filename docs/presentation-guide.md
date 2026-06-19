# Project Presentation Guide

This guide is written for project walkthroughs, portfolio reviews, technical discussions, and AI Agent product demos. It explains how to present OpenCode Harness clearly without over-claiming.

## 1-Minute Pitch

OpenCode Harness is a clean-room, model-agnostic AI coding agent harness. The problem it addresses is that many coding-agent demos look impressive, but they are hard to reproduce, compare, or diagnose. The project defines a standardized workflow: Task Input -> Planning -> Tool Execution -> Review -> Report.

The harness supports DeepSeek, Qwen, Claude, OpenAI, local OpenAI-compatible endpoints, vLLM, SGLang, Ollama, and mock mode. It includes permissioned tools, MCP-compatible extension points, JSONL traces, provider transcripts, eval suites, reports, and dashboards.

The product value is that it turns coding-agent behavior from an opaque chat interaction into observable evidence. The DeepSeek Lab case study uses real DeepSeek API benchmarks across smoke, long-context, and repair suites. The results are not presented as a leaderboard; they are used to diagnose failure modes such as marker drift, tool-loop overrun, long-context synthesis gaps, and repair finalization gaps.

## 3-Minute Pitch

OpenCode Harness is an open-source AI coding agent harness built to explore how Claude Code / Codex-class coding agents can be standardized and evaluated. It is intentionally positioned as a clean-room implementation, so it does not use or derive from any proprietary Claude Code source. The focus is the infrastructure layer: how an agent receives a coding task, plans, calls tools, observes results, verifies completion, and produces reports.

The target users are AI product managers, agent engineers, model evaluation teams, and people building local model workflows. The user pain point is that coding-agent demos are often hard to trust: you see the final answer, but not always the tool calls, permissions, intermediate state, traces, or failure reasons. OpenCode Harness solves this by defining a repeatable workflow: Task Input -> Planning -> Tool Execution -> Review -> Report.

Technically, the project includes a model-neutral provider layer for DeepSeek, Qwen, Claude, OpenAI, local OpenAI-compatible servers, vLLM, SGLang, Ollama, and mock mode. It has a permissioned tool system for file operations, search, patching, shell commands, repo maps, context packing, todos, and finish events. It also supports MCP-compatible extension points for external tools, resources, prompts, and per-server approvals.

For evaluation and observability, it writes JSONL traces, provider transcripts, Markdown/HTML reports, comparison reports, and dashboards. This means a user can inspect not only whether the agent passed a task, but also how it behaved and why it failed.

DeepSeek Lab is the main case study. It uses real DeepSeek API benchmarks across smoke, long-context, and repair suites. The results showed several failure modes: marker-following drift, tool-loop overrun, long-context synthesis gaps, and repair finalization gaps. These failures are published intentionally, because the product value of the harness is diagnosis and repeatability, not just showing a perfect demo.

From an AI product perspective, this project demonstrates product framing, user pain point analysis, workflow design, evaluation metrics, launch packaging, and failure-mode communication. From an AI Agent application perspective, it demonstrates provider abstraction, tool orchestration, permission policy, traceability, evaluation design, and real provider testing.

## Discussion Q&A

1. **What problem does this project solve?**
   It solves the lack of reproducibility, observability, and structured evaluation in coding-agent demos.

2. **Who are the target users?**
   AI PMs, AI agent engineers, model evaluation teams, local model users, and technical demo audiences.

3. **Why call it a harness?**
   Because it wraps model calls, tools, permissions, traces, evals, and reports into a standardized execution environment.

4. **How is it different from a coding assistant?**
   A coding assistant focuses on helping a user code. This harness focuses on running, observing, evaluating, and diagnosing the agent workflow.

5. **Is this a Claude Code clone?**
   No. It is a clean-room implementation of a coding-agent harness and does not contain or derive from proprietary source code.

6. **Why model-agnostic?**
   Agent workflows should be comparable across providers. Provider abstraction lets the same suite run against DeepSeek, Qwen, Claude, OpenAI, or local models.

7. **What is the core workflow?**
   Task Input -> Planning -> Tool Execution -> Review -> Report.

8. **What tools does the agent have?**
   File read/write, text search, patching, shell, git diff, repo map, context pack, todo, finish, and MCP-compatible external tools.

9. **How do you control risky operations?**
   Through permission policy for writes, shell commands, network actions, approval mode, and MCP per-server approvals.

10. **What does MCP-compatible mean here?**
   The harness can connect stdio MCP-style tools/resources/prompts and expose them to the agent with namespacing and lifecycle diagnostics.

11. **What does the eval system produce?**
   JSONL traces, session files, `report.json`, `report.md`, `report.html`, comparison reports, and dashboards.

12. **Why are traces important?**
   They make model behavior auditable: prompts, provider payloads, responses, tool calls, tool results, and timing can be inspected.

13. **How do you evaluate success?**
   Each eval case can check expected output markers, verification commands, completion status, failure type, steps, and timing.

14. **What did DeepSeek Lab show?**
   It showed that real DeepSeek coding-agent runs can be diagnosed into failure modes such as marker drift, tool-loop overrun, long-context synthesis gaps, and repair finalization gaps.

15. **Why publish failed benchmark results?**
   Because the project value is diagnosis. Publishing failures proves the harness can surface real agent reliability issues instead of only showing cherry-picked demos.

16. **What would you improve next?**
   The final-step guard, finish-marker reminder, and diagnosis report are in place; next I would improve repair verification feedback and before/after benchmark comparison.

17. **What product metrics would you track?**
   Pass rate, failure type distribution, average steps, total runtime, tool-call count, verification success, and repeated failure patterns.

18. **What is the business or product value?**
   It helps teams compare providers, debug agent workflows, reduce opaque failures, and make model/provider decisions with evidence.

19. **How would this become a real product?**
   Add a hosted dashboard, task library, scheduled evals, team workspaces, artifact storage, and GitHub PR/issue integrations.

20. **What does this project demonstrate?**
   It demonstrates the connection between AI product thinking and agent engineering: user pain points, workflow design, model integration, tool safety, evaluation, diagnosis, documentation, and launch packaging.
