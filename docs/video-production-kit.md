# Video Production Kit

This kit turns the 75-second script into a repeatable recording workflow.

## Goal

Produce a short product demo for the website, Product Hunt, GitHub README, and social posts.

Target runtime:

```text
75 seconds
```

Primary message:

```text
OpenCode Harness is a clean-room eval harness for coding agents across DeepSeek, Qwen, Claude, OpenAI, and local models.
```

## Generate Demo Artifacts

From the repository root:

```powershell
.\scripts\recording-demo.ps1
```

If `python` does not point to a Python 3.11+ environment:

```powershell
.\scripts\recording-demo.ps1 -Python "C:\Path\To\python.exe"
```

Generated files live under:

```text
eval-runs/recording-demo/
```

Expected outputs:

- `01-version.txt`
- `02-eval.txt`
- `03-replay.txt`
- `04-tui.txt`
- `05-trace-html.txt`
- `06-dashboard.txt`
- `latest-trace.html`
- `dashboard.html`
- `**/*.jsonl`
- `**/report.html`

## Recording Setup

Screen:

- 16:9 canvas.
- 1920x1080 preferred.
- Browser zoom: 100%.
- Terminal font: 16-18 px.
- Terminal width: at least 100 columns.
- Hide desktop notifications.

Browser tabs:

1. Website: `https://samarailly51-pixel.github.io/opencode-harness/`
2. GitHub repo: `https://github.com/samarailly51-pixel/opencode-harness`
3. Release: `https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0`
4. Local trace HTML: `eval-runs/recording-demo/latest-trace.html`
5. Local dashboard: `eval-runs/recording-demo/dashboard.html`

Terminal commands to show:

```powershell
python -m opencode_harness version
python -m opencode_harness eval examples/mock-suite.json --preset mock --max-steps 2 --context-chars 1000
python -m opencode_harness tui <latest inspect-repo trace> --width 88
python -m opencode_harness trace-html <latest inspect-repo trace> --output eval-runs/recording-demo/latest-trace.html
python -m opencode_harness dashboard eval-runs/recording-demo --output eval-runs/recording-demo/dashboard.html
```

## Shot List

| Time | Shot | Visual | Voiceover |
| --- | --- | --- | --- |
| 0-8s | Problem | Provider names and inconsistent demo surfaces | Coding agents are everywhere, but comparing them is messy. Each demo uses different tools, prompts, and traces. |
| 8-18s | Product reveal | Website hero, then terminal eval command | OpenCode Harness gives coding agents a shared runtime: one agent loop, one tool layer, one trace format, and one eval surface. |
| 18-34s | Runtime | Provider presets and CLI help | Run the same workflow across DeepSeek, Qwen, Claude, OpenAI, vLLM, SGLang, Ollama, and OpenAI-compatible local endpoints. |
| 34-50s | Tools and MCP | README feature section or diagram overlay | The harness includes permissioned tools and MCP-compatible extension points for tools, resources, prompts, diagnostics, and approvals. |
| 50-64s | Evaluation surface | Terminal trace viewer, trace HTML, dashboard | Every run produces JSONL traces, provider transcripts, replay summaries, HTML reports, a terminal trace viewer, and an eval dashboard. |
| 64-75s | Call to action | GitHub release and website final frame | OpenCode Harness v0.1.0 is open source now. Use it to test, compare, and debug coding agents across model providers. |

## Lower-Third Text

Use these short overlays:

```text
Same task. Same tools. Comparable traces.
Model-neutral runtime for coding agents.
MCP-compatible extension points.
JSONL traces, transcripts, reports, dashboards.
Open-source v0.1.0 release.
```

## Export Settings

Recommended:

- Format: MP4.
- Codec: H.264.
- Resolution: 1920x1080.
- Frame rate: 30 fps.
- Audio: AAC, 48 kHz.
- Target length: 60-75 seconds.

Also export:

- 15-second teaser.
- Silent version with burned-in captions.
- Thumbnail using `site/assets/product-hunt-gallery-1.png`.

## Review Checklist

- The first 3 seconds clearly show the product category.
- No terminal command is visible long enough to look broken.
- The site URL and GitHub URL are visible near the end.
- The video avoids proprietary-source or clone claims.
- All claims are supported by current repository features.
- Captions fit mobile screens.
- Final frame holds for at least 2 seconds.

## Files

- Script: [promo-video-script.md](promo-video-script.md)
- Captions: [video-captions.srt](video-captions.srt)
- Product Hunt launch kit: [launch-kit.md](launch-kit.md)
- Website deployment: [website-deployment.md](website-deployment.md)
