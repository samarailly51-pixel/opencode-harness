# Launch Kit

This kit turns OpenCode Harness from "a solid GitHub project" into a launchable product story.

For the current go/no-go state, see [launch-readiness.md](launch-readiness.md).

## Product Hunt Listing

Product name:

```text
OpenCode Harness
```

Tagline:

```text
Eval harness for coding agents across model providers
```

Short description:

```text
OpenCode Harness is an open-source, clean-room evaluation harness for coding agents. Run the same workflow across DeepSeek, Qwen, Claude, OpenAI, vLLM, SGLang, Ollama, and local OpenAI-compatible models, then inspect traces, tool calls, transcripts, reports, and dashboards.
```

Topics:

```text
Developer Tools, Artificial Intelligence, Open Source
```

Primary links:

```text
Website: https://samarailly51-pixel.github.io/opencode-harness/
GitHub: https://github.com/samarailly51-pixel/opencode-harness
Release: https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0
Demo report: https://github.com/samarailly51-pixel/opencode-harness/tree/master/benchmarks/v0.1-mock-smoke
```

## Maker Comment

```text
Hi Product Hunt,

I built OpenCode Harness because coding-agent demos are easy to make, but hard to compare fairly.

Most agent projects mix together a model, prompts, tools, traces, and evaluation logic. That makes it difficult to answer simple questions like:

- Did this model actually solve the task?
- Which tool calls did it make?
- What did the provider request and response look like?
- Can I replay the trace and compare another model on the same workflow?

OpenCode Harness is a clean-room runtime and eval layer for coding agents. It supports provider presets for DeepSeek, Qwen, Claude, OpenAI, local OpenAI-compatible endpoints, vLLM, SGLang, Ollama, and mock mode. It includes permissioned tools, MCP-compatible extension points, JSONL traces, provider transcripts, HTML reports, a terminal trace viewer, and an eval dashboard.

The goal is not to clone any proprietary agent. The goal is to create open infrastructure for testing, debugging, and comparing coding agents.

I would love feedback from people building agents, evaluating models, or running local coding models.
```

## Gallery Assets

Product Hunt preparation notes checked on 2026-06-11:

- Tagline limit: 60 characters.
- Description limit: 500 characters.
- Topic limit: 3 topics.
- Thumbnail recommendation: `240x240`, under 3 MB.
- Gallery requirement: at least 2 images.
- Gallery recommendation: `1270x760`.

Keep the first gallery image readable at thumbnail size.

Prepared assets:

- `site/assets/product-hunt-gallery-1.png`
- `site/assets/product-hunt-gallery-2.png`
- `site/assets/product-hunt-logo.png`
- `site/assets/product-hunt-thumbnail.png`
- `media/demo-video/opencode-harness-demo.mp4`
- `media/demo-video/opencode-harness-demo-thumbnail.png`

Suggested ordering:

1. Hero positioning: model-neutral coding-agent eval harness.
2. Trace and dashboard proof: tool calls, transcripts, pass rates, reports.

## Video Assets

Use [promo-video-script.md](promo-video-script.md) as the main 75-second script, and [video-production-kit.md](video-production-kit.md) for the recording workflow, captions, and shot list.

Minimum recording sequence:

1. Website hero.
2. Terminal mock eval.
3. JSONL trace opening in terminal viewer.
4. HTML report or trace viewer.
5. Eval dashboard.
6. GitHub release page.

## Launch-Day Posts

### X / Twitter

```text
I just launched OpenCode Harness v0.1.0.

It is an open-source, clean-room eval harness for coding agents across DeepSeek, Qwen, Claude, OpenAI, and local models.

Run the same workflow, inspect traces/tool calls/transcripts, and compare results.

Website: https://samarailly51-pixel.github.io/opencode-harness/
GitHub: https://github.com/samarailly51-pixel/opencode-harness
```

### LinkedIn

```text
I launched OpenCode Harness, an open-source evaluation harness for coding agents.

The project focuses on the infrastructure layer: a shared agent loop, permissioned tools, MCP-compatible extension points, provider presets, JSONL traces, provider transcripts, replay tooling, HTML reports, and an eval dashboard.

The goal is to make coding-agent behavior easier to test, compare, and debug across DeepSeek, Qwen, Claude, OpenAI, and local model providers.

Website: https://samarailly51-pixel.github.io/opencode-harness/
Repo: https://github.com/samarailly51-pixel/opencode-harness
```

### GitHub Discussion / Community Post

```text
I released OpenCode Harness v0.1.0, a clean-room evaluation harness for coding agents.

It supports provider presets, permissioned tools, MCP-compatible tool extension points, JSONL traces, provider transcripts, replay summaries, HTML reports, and an eval dashboard.

I am looking for feedback from people building model evals, local coding-agent workflows, and provider comparison tooling.
```

## Launch Checklist

Pre-launch:

- Confirm README has a crisp first screen.
- Confirm v0.1.0 release assets are downloadable.
- Confirm CI is green on `master`.
- Deploy `site/` to a public URL.
- Confirm the public demo report is linked from README.
- Record the 75-second demo video.
- Upload at least two Product Hunt gallery images.
- Prepare maker comment and launch-day posts.
- Make sure the Product Hunt maker account is complete well before launch day.

Launch day:

- Publish Product Hunt post.
- Share the launch link without asking for artificial upvotes.
- Reply to comments quickly and specifically.
- Pin the best demo video or dashboard screenshot on social profiles.
- Capture feedback in issues or a public roadmap.

Post-launch:

- Add the Product Hunt badge or link after the launch is live.
- Create issues for repeated feedback.
- Publish a short benchmark/demo report.
- Tag the next patch release if launch feedback uncovers simple fixes.

## Positioning Rules

Use:

- "Clean-room coding-agent eval harness"
- "Model-neutral agent runtime"
- "Compare DeepSeek, Qwen, Claude, OpenAI, and local models"
- "Traceable tool calls, provider transcripts, reports, dashboards"

Avoid:

- Claims that imply proprietary-source reuse.
- "Claude Code clone" as the headline.
- Unsupported benchmark superiority claims.
- Asking people to upvote.

## References

- Product Hunt launch guide: https://www.producthunt.com/launch
- Product Hunt preparation guide: https://www.producthunt.com/launch/preparing-for-launch
