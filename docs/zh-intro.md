# OpenCode Harness 中文介绍

OpenCode Harness 是一个开源的 AI coding agent 运行与评测框架。它不是复刻 Claude Code，也不复用任何闭源实现，而是用 clean-room 的方式实现一套模型中立的 agent runtime：同一套任务、工具、权限、trace、eval suite 和报告系统，可以接 DeepSeek、Qwen、Claude、OpenAI、本地 OpenAI-compatible 服务、vLLM、SGLang、Ollama 等模型后端。

一句话概括：

```text
OpenCode Harness 把 coding agent 从一次性的 demo，变成可复现、可追踪、可对比、可诊断的工程系统。
```

## 解决什么问题

很多 coding agent demo 看起来很酷，但很难回答几个关键问题：

- 模型到底有没有完成任务？
- 它调用了哪些工具？
- 它读了哪些文件、尝试了哪些命令、产生了什么中间状态？
- 同一个任务换成另一个模型，结果是否还能比较？
- 失败时，是模型能力问题、工具循环没收住、权限被拦截，还是评测断言太窄？

OpenCode Harness 关注的是这些基础设施问题。它提供统一的 agent loop、工具层、权限模型、trace 格式、eval 报告和 failure-mode diagnosis，让不同模型可以在同一个评测表面上运行。

## 核心能力

- **模型中立 provider 架构**：支持 DeepSeek、Qwen、Claude、OpenAI、本地模型和 mock provider。
- **权限控制工具系统**：文件读取、搜索、补丁、shell、repo map、context pack、todo、finish 等工具都有清晰边界。
- **MCP-compatible 扩展点**：支持 stdio MCP tools/resources/prompts、per-server approval、生命周期诊断和命名冲突处理。
- **可审计 trace**：每次模型响应、工具调用、命令输出和 session 状态都能写入 JSONL trace。
- **可复现 eval**：用 JSON suite 定义任务，自动产出 `report.json`、`report.md`、`report.html` 和 comparison report。
- **Trace-aware diagnosis**：从 eval report 和 JSONL trace 中提取 repeated tool、failed tools、marker 状态和 no-finish event。
- **Before/after comparison**：用 `diagnose-compare` 比较可靠性改动前后的 pass rate、failure type、trace signal 和 case outcome。
- **Model Labs**：为 DeepSeek、Qwen、Claude、OpenAI、本地模型分别建立可扩展评测目录。

## DeepSeek Lab 做了什么

项目重点做了 DeepSeek Lab，并用真实 DeepSeek API 跑了三类 benchmark：

| Suite | 结果 | 主要暴露的问题 |
| --- | ---: | --- |
| Smoke | 1/4 passed | marker 遵循不稳定、工具循环收尾弱 |
| Long context | 1/4 passed | 长上下文综合不稳定、部分 case 触发 `max_steps` |
| Repair | 0/2 passed | 修改、验证、完成标记的闭环不稳定 |

这些结果不是为了做 DeepSeek 排行榜，也不是为了简单判断某个模型好坏。它们的价值在于：OpenCode Harness 能把 coding agent 的失败拆成具体模式，例如：

- marker-following drift：没有按要求输出完成标记。
- tool-loop overrun：一直想继续检查文件，没有及时收尾。
- long-context synthesis gap：能解释局部模块，但跨模块综合不稳定。
- repair finalization gap：可能修改了文件，但没有稳定完成测试验证与最终总结。
- repeated tail tools：trace 末尾反复调用同类工具，例如连续 `read_file`。
- failed tools：repair 任务里工具失败或权限问题会被单独标出来，避免把所有问题都归因给模型。

完整分析见：[DeepSeek failure-mode diagnosis](deepseek-failure-mode-diagnosis.md)。

## 为什么不是 Claude Code clone

OpenCode Harness 不包含、也不派生自 Claude Code 源码。项目采用 clean-room 边界，只基于公开模型 API、公开工具协议、可观察行为和自主实现的 agent runtime。

更准确的定位是：

```text
一个用于构建、运行和评测 Claude Code-class / Codex-class coding agent 的开源 harness。
```

也就是说，它借鉴的是“coding agent 应该具备哪些工程能力”这个问题空间，而不是复用任何闭源实现。

## 如何运行

离线 mock demo，不需要 API key：

```powershell
$env:PYTHONPATH='src'
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
```

运行 DeepSeek-only benchmark：

```powershell
$env:DEEPSEEK_API_KEY = "..."
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet all
```

生成 trace-aware diagnosis：

```powershell
python -m opencode_harness diagnose `
  eval-runs/path-to-run/report.json `
  --output eval-runs/diagnosis.md
```

比较改动前后的可靠性变化：

```powershell
python -m opencode_harness diagnose-compare `
  --before eval-runs/before/report.json `
  --after eval-runs/after/report.json `
  --before-label "Before guard" `
  --after-label "After guard" `
  --output eval-runs/before-after.md
```

相关报告：

- [Real provider comparison](../benchmarks/real-provider-comparison/README.md)
- [DeepSeek smoke report](../model-labs/deepseek/reports/provider-comparison.md)
- [DeepSeek long-context report](../model-labs/deepseek/reports/long-context-comparison.md)
- [DeepSeek repair report](../model-labs/deepseek/reports/repair-comparison.md)
- [Website case study](https://samarailly51-pixel.github.io/opencode-harness/deepseek-case-study.html)

## 适合怎么介绍

30 秒版本：

```text
OpenCode Harness 是我做的一个开源 coding agent 评测框架。它不是复刻 Claude Code，而是用 clean-room 的方式实现一套模型中立的 agent runtime：同一套工具调用、权限控制、trace、eval suite 和报告系统，可以接 DeepSeek、Qwen、Claude、OpenAI 或本地模型。我重点做了 DeepSeek Lab，用真实 DeepSeek API 跑了 smoke、long-context 和 repair 三类 benchmark，并把失败结果整理成 trace-aware failure-mode diagnosis，用来定位模型在 agent 场景下的工具循环、长上下文和代码修复问题。
```

简历版本：

```text
Built OpenCode Harness, a clean-room coding-agent runtime and evaluation harness with multi-provider adapters, MCP-compatible tool extensions, permissioned tools, JSONL traces, reproducible eval reports, trace-aware diagnosis, before/after reliability comparison, and a DeepSeek failure-mode case study.
```

## 当前状态

项目已经具备公开展示条件：

- GitHub repo、CI、release、GitHub Pages 已完成。
- DeepSeek-only 真实 benchmark 已发布。
- DeepSeek trace-aware failure-mode diagnosis 和网站案例页已完成。
- `diagnose-compare` 已支持 before/after reliability comparison。
- Product Hunt package、demo video draft 和 launch readiness 已准备好。

下一步最有价值的是重新跑 DeepSeek benchmark，把 finish-marker reminder、final-step guard、trace-aware diagnosis 和 before/after comparison 串成一份真实可靠性迭代案例。
