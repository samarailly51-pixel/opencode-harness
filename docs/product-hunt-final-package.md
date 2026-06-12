# Product Hunt Final Package

Last checked against the Product Hunt launch guide: 2026-06-12.

This is the copy/paste package for launching OpenCode Harness on Product Hunt.

## Submission Fields

Product URL:

```text
https://samarailly51-pixel.github.io/opencode-harness/
```

Product name:

```text
OpenCode Harness
```

Tagline:

```text
Eval harness for coding agents across model providers
```

Description:

```text
OpenCode Harness is an open-source, clean-room evaluation harness for coding agents. Run the same workflow across DeepSeek, Qwen, Claude, OpenAI, vLLM, SGLang, Ollama, and local OpenAI-compatible models, then inspect traces, tool calls, transcripts, reports, and dashboards.
```

Launch tags:

```text
Developer Tools
Artificial Intelligence
Open Source
```

Pricing:

```text
Free
```

Additional links:

```text
GitHub: https://github.com/samarailly51-pixel/opencode-harness
Release: https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0
Demo report: https://github.com/samarailly51-pixel/opencode-harness/tree/master/benchmarks/v0.1-mock-smoke
DeepSeek diagnostic benchmark: https://github.com/samarailly51-pixel/opencode-harness/tree/master/benchmarks/real-provider-comparison
DeepSeek case study: https://samarailly51-pixel.github.io/opencode-harness/deepseek-case-study.html
```

Video URL:

```text
TODO: Upload media/demo-video/opencode-harness-demo.mp4 to YouTube and paste the full public or unlisted YouTube URL here.
```

Product Hunt only supports YouTube links for videos. Do not use a shortened URL.

## Upload Assets

Thumbnail:

```text
site/assets/product-hunt-thumbnail.png
```

Gallery images, in order:

```text
site/assets/product-hunt-gallery-1.png
site/assets/product-hunt-gallery-2.png
site/assets/dashboard-preview.png
site/assets/trace-preview.png
```

Video source:

```text
media/demo-video/opencode-harness-demo.mp4
```

Video thumbnail:

```text
media/demo-video/opencode-harness-demo-thumbnail.png
```

## Maker First Comment

```text
Hi Product Hunt,

I built OpenCode Harness because coding-agent demos are easy to make, but hard to compare fairly.

Most agent projects mix together a model, prompts, tools, traces, and evaluation logic. That makes it difficult to answer simple questions:

- Did this model actually solve the task?
- Which tool calls did it make?
- What did the provider request and response look like?
- Can I replay the trace and compare another model on the same workflow?

OpenCode Harness is a clean-room runtime and eval layer for coding agents. It supports provider presets for DeepSeek, Qwen, Claude, OpenAI, local OpenAI-compatible endpoints, vLLM, SGLang, Ollama, and mock mode.

It includes permissioned tools, MCP-compatible extension points, JSONL traces, provider transcripts, HTML reports, a terminal trace viewer, an eval dashboard, a public no-key demo report, a DeepSeek failure-mode case study, and a 75-second demo video.

The goal is not to clone any proprietary agent. The goal is to create open infrastructure for testing, debugging, and comparing coding agents.

I would love feedback from people building agents, evaluating models, or running local coding models.
```

## Social Posts

### X / Twitter

```text
I launched OpenCode Harness v0.1.0.

It is an open-source, clean-room eval harness for coding agents across DeepSeek, Qwen, Claude, OpenAI, and local models.

Run the same workflow, inspect traces/tool calls/transcripts, and compare results.

Website: https://samarailly51-pixel.github.io/opencode-harness/
GitHub: https://github.com/samarailly51-pixel/opencode-harness
```

Launch-day version after Product Hunt URL is live:

```text
OpenCode Harness is live on Product Hunt.

It is a clean-room eval harness for coding agents across DeepSeek, Qwen, Claude, OpenAI, and local models.

I would love feedback from people building agents and model evals:

TODO_PRODUCT_HUNT_URL
```

### LinkedIn

```text
I launched OpenCode Harness, an open-source evaluation harness for coding agents.

The project focuses on the infrastructure layer: a shared agent loop, permissioned tools, MCP-compatible extension points, provider presets, JSONL traces, provider transcripts, replay tooling, HTML reports, an eval dashboard, and a public demo report.

The goal is to make coding-agent behavior easier to test, compare, and debug across DeepSeek, Qwen, Claude, OpenAI, and local model providers.

Website: https://samarailly51-pixel.github.io/opencode-harness/
Repo: https://github.com/samarailly51-pixel/opencode-harness
```

### GitHub Discussion

```text
I released OpenCode Harness v0.1.0, a clean-room evaluation harness for coding agents.

It supports provider presets, permissioned tools, MCP-compatible tool extension points, JSONL traces, provider transcripts, replay summaries, HTML reports, an eval dashboard, a no-key public demo report, and a 75-second demo video.

I am looking for feedback from people building model evals, local coding-agent workflows, and provider comparison tooling.
```

## Launch-Day Sequence

Before scheduling:

- Confirm the Product Hunt maker account is complete.
- Upload `media/demo-video/opencode-harness-demo.mp4` to YouTube.
- Paste the YouTube URL into the Product Hunt video field.
- Confirm the website loads and video plays.
- Confirm CI is green.
- Confirm the v0.1.0 release assets are downloadable.
- Confirm the demo report link opens.

Scheduling:

- Product Hunt lets makers schedule launches up to 1 month ahead.
- If there is no other timing constraint, schedule for `12:01am Pacific Time`.
- Choose a time you can monitor comments for several hours.

Launch day:

- Publish or let the scheduled launch go live.
- Share the launch link and ask for feedback or comments, not upvotes.
- Reply to every useful comment with specific context.
- Pin the website/demo video on social profiles.
- Capture repeated feedback into GitHub issues.

After launch:

- Add Product Hunt URL to README and launch readiness.
- Add Product Hunt badge if useful.
- Create follow-up issues for repeated feedback.
- Tighten the DeepSeek failure modes surfaced by the diagnostic benchmark set.

## Compliance Checks

Product Hunt field checks:

- Product name contains only the product name.
- Tagline is under 60 characters.
- Description is under 500 characters.
- Launch tags are 3 or fewer.
- Thumbnail is square, `240x240`, and under 3 MB.
- Gallery includes at least 2 images.
- Gallery images use the recommended `1270x760` size where possible.
- Video is a full YouTube URL and is not private.
- Posts ask for feedback, not upvotes.

Project positioning checks:

- Uses "clean-room" accurately.
- Does not imply proprietary-source reuse.
- Does not claim broad provider ranking from the DeepSeek diagnostic benchmark set.
- Treats the mock benchmark as a harness smoke benchmark, not a model-quality benchmark.

## Official References

- Product Hunt launch guide: https://www.producthunt.com/launch
- Product Hunt preparation guide: https://www.producthunt.com/launch/preparing-for-launch
