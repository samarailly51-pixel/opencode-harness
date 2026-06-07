# Local Model Lab

Local Model Lab evaluates self-hosted OpenAI-compatible coding-agent backends such as vLLM, SGLang, Ollama OpenAI bridges, and custom local gateways.

The goal is to compare local deployments against DeepSeek, Qwen, Claude, and OpenAI using the same agent loop, tool schemas, permissions, traces, and eval reports.

## Scope

- Local OpenAI-compatible endpoint routing.
- vLLM, SGLang, and Ollama preset behavior.
- Native OpenAI-compatible tool calls.
- JSON fallback behavior.
- Repository-context synthesis under local context limits.
- Provider transcript auditability for self-hosted runs.
- Chinese and bilingual coding tasks.

## Presets

| Preset | Default Base URL | Default Model | API Key Env |
| --- | --- | --- | --- |
| `local-openai` | `http://localhost:8000` | `local-coder` | `LOCAL_MODEL_API_KEY` |
| `vllm` | `http://localhost:8000` | `local-coder` | `VLLM_API_KEY` |
| `sglang` | `http://localhost:30000` | `local-coder` | `SGLANG_API_KEY` |
| `ollama` | `http://localhost:11434` | `qwen2.5-coder:7b` | `OLLAMA_API_KEY` |

Many local servers accept any bearer token. Set the relevant environment variable to `dummy` when the server does not require authentication.

## Run

Use the mock provider for lab wiring smoke testing:

```powershell
python -m opencode_harness eval model-labs/local/mock-smoke-suite.json --preset mock --max-steps 2
```

Run a local OpenAI-compatible endpoint:

```powershell
$env:LOCAL_MODEL_API_KEY = "dummy"
python -m opencode_harness eval model-labs/local/local-coding-agent-suite.json --preset local-openai --model "your-local-model" --max-steps 8 --context-chars 8000
```

Run provider comparison across local runtimes:

```powershell
python -m opencode_harness lab-compare `
  model-labs/local/local-coding-agent-suite.json `
  --presets local-openai vllm sglang ollama `
  --max-steps 8 `
  --context-chars 8000 `
  --comparison-output model-labs/local/reports/provider-comparison.md
```

By default, providers with missing API key environment variables are skipped and listed in the generated comparison.

## Outputs

Eval runs write per-case traces, sessions, `report.json`, `report.md`, and `report.html` under `eval-runs/`.

Use replay to inspect failures:

```powershell
python -m opencode_harness replay eval-runs/<run>/<case>.jsonl --show-content
```

## Clean-Room Boundary

This lab only uses public API compatibility behavior and authorized local deployments. It does not use leaked, proprietary, or unauthorized source code.
