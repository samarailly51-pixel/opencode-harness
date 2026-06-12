# Launch Readiness

Last checked: 2026-06-12, Asia/Shanghai.

This page is the single launch control panel for OpenCode Harness.

## Current Verdict

OpenCode Harness is ready for a soft public launch as an open-source v0.1 project.

Use the current positioning:

```text
OpenCode Harness is a clean-room, model-neutral evaluation harness for coding agents across DeepSeek, Qwen, Claude, OpenAI, and local models.
```

Do not position it as a proprietary-agent clone or as a model leaderboard until real provider runs have been published.

## Live Assets

| Asset | Status | Link |
| --- | --- | --- |
| GitHub repo | Ready | <https://github.com/samarailly51-pixel/opencode-harness> |
| Website | Ready | <https://samarailly51-pixel.github.io/opencode-harness/> |
| v0.1.0 release | Ready | <https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0> |
| Public demo report | Ready | [benchmarks/v0.1-mock-smoke](../benchmarks/v0.1-mock-smoke/README.md) |
| Product Hunt kit | Ready | [launch-kit.md](launch-kit.md) |
| Demo video draft | Ready | [media/demo-video](../media/demo-video/README.md), embedded in website |
| Video production kit | Ready | [video-production-kit.md](video-production-kit.md) |
| Provider benchmark guide | Ready | [provider-benchmarks.md](provider-benchmarks.md) |

## Verified State

| Check | Status | Evidence |
| --- | --- | --- |
| Last checked commit | Ready | `afd684e5d2dfaa04b453900b84a32b07207b49d8` |
| Last checked CI | Passing | <https://github.com/samarailly51-pixel/opencode-harness/actions/runs/27359763808> |
| Website HTTP | Passing | `200`, title `OpenCode Harness - Evaluation Harness for Coding Agents` |
| GitHub Pages | Passing | workflow deployment enabled |
| Release | Published | `v0.1.0`, not draft, not prerelease |
| Wheel asset | Published | `opencode_harness-0.1.0-py3-none-any.whl` |
| Source asset | Published | `opencode_harness-0.1.0.tar.gz` |
| Public benchmark | Published | harness smoke benchmark, not model ranking |

## Launch Checklist

Ready:

- [x] Clean-room positioning.
- [x] Public GitHub repository.
- [x] v0.1.0 release.
- [x] Wheel and source distribution assets.
- [x] CI passing.
- [x] GitHub Pages website.
- [x] README first-screen product positioning.
- [x] Product Hunt listing copy.
- [x] Product Hunt gallery assets.
- [x] Product Hunt thumbnail.
- [x] Promo video script.
- [x] SRT captions.
- [x] Recording/demo generation script.
- [x] Public no-key demo benchmark report.

Still needed before a bigger launch:

- [x] Render a silent 75-second demo video draft.
- [ ] Record or add voiceover for the 60-75 second demo video.
- [ ] Publish at least one real provider comparison if API keys are available.
- [ ] Add a Product Hunt badge/link after Product Hunt is live.
- [ ] Optionally connect a custom domain.

## Launch Sequence

1. Record the demo with [video-production-kit.md](video-production-kit.md).
2. Upload the video to the launch page and social post drafts.
3. Use [launch-kit.md](launch-kit.md) for Product Hunt title, tagline, description, maker comment, and social posts.
4. Link the public demo report as the reproducible evidence artifact.
5. After launch, collect feedback into GitHub issues or the roadmap.

## Risk Notes

- The public benchmark is a mock smoke benchmark. It proves the harness artifact flow, not real model quality.
- The project should avoid claims like "better than Claude Code" or "DeepSeek V4 reversed" unless backed by clean-room, reproducible, real-provider reports.
- The safe framing is infrastructure: shared runtime, permissioned tools, traces, transcripts, reports, dashboards, and model-provider comparison workflow.

## Next Best Work

The next highest-value work is adding voiceover to the rendered demo video or running a real provider benchmark:

```powershell
python -m opencode_harness lab-compare `
  model-labs/deepseek/deepseek-v4-suite.json `
  --presets deepseek qwen openai claude `
  --comparison-output model-labs/deepseek/reports/provider-comparison.md
```

If API keys are unavailable, the next best work is recording the demo video from the existing no-key artifacts.
