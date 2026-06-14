# Launch Readiness

Last checked: 2026-06-12, Asia/Shanghai.

This page is the single launch control panel for OpenCode Harness.

## Current Verdict

OpenCode Harness is ready for a soft public launch as an open-source v0.1 project.

A first DeepSeek-only real-provider benchmark set has been published. Treat it
as a diagnostic harness result, not as a broad provider ranking.

Use the current positioning:

```text
OpenCode Harness is a clean-room, model-neutral evaluation harness for coding agents across DeepSeek, Qwen, Claude, OpenAI, and local models.
```

Do not position it as a proprietary-agent clone or as a full model leaderboard.
The published real-provider results are currently DeepSeek-only smoke,
long-context, and repair runs. The current benchmark direction is DeepSeek-only
depth before cross-provider breadth.

## Live Assets

| Asset | Status | Link |
| --- | --- | --- |
| GitHub repo | Ready | <https://github.com/samarailly51-pixel/opencode-harness> |
| Website | Ready | <https://samarailly51-pixel.github.io/opencode-harness/> |
| v0.1.0 release | Ready | <https://github.com/samarailly51-pixel/opencode-harness/releases/tag/v0.1.0> |
| Chinese introduction | Ready | [zh-intro.md](zh-intro.md) |
| Product positioning | Ready | [product-positioning.md](product-positioning.md) |
| Presentation guide | Ready | [presentation-guide.md](presentation-guide.md) |
| Demo workflow | Ready | [examples/demo-workflow.md](../examples/demo-workflow.md) |
| Public demo report | Ready | [benchmarks/v0.1-mock-smoke](../benchmarks/v0.1-mock-smoke/README.md) |
| Real provider benchmark package | Ready, DeepSeek-only benchmark set published | [real-provider-comparison](../benchmarks/real-provider-comparison/README.md) |
| DeepSeek case study | Ready | [deepseek-failure-mode-diagnosis.md](deepseek-failure-mode-diagnosis.md), <https://samarailly51-pixel.github.io/opencode-harness/deepseek-case-study.html> |
| Product Hunt kit | Ready | [launch-kit.md](launch-kit.md) |
| Product Hunt final package | Ready | [product-hunt-final-package.md](product-hunt-final-package.md) |
| Demo video draft | Ready | [media/demo-video](../media/demo-video/README.md), embedded in website |
| Video production kit | Ready | [video-production-kit.md](video-production-kit.md) |
| Provider benchmark guide | Ready | [provider-benchmarks.md](provider-benchmarks.md) |

## Verified State

| Check | Status | Evidence |
| --- | --- | --- |
| Repository head | Ready | CI badge tracks current `master` |
| CI workflow | Passing | <https://github.com/samarailly51-pixel/opencode-harness/actions/workflows/ci.yml> |
| Website HTTP | Passing | `200`, title `OpenCode Harness - Evaluation Harness for Coding Agents` |
| GitHub Pages | Passing | workflow deployment enabled |
| Release | Published | `v0.1.0`, not draft, not prerelease |
| Wheel asset | Published | `opencode_harness-0.1.0-py3-none-any.whl` |
| Source asset | Published | `opencode_harness-0.1.0.tar.gz` |
| Public benchmark | Published | harness smoke benchmark, not model ranking |
| Real provider benchmark | Published | DeepSeek `deepseek-chat`: smoke 1/4, long-context 1/4, repair 0/2 |

## Launch Checklist

Ready:

- [x] Clean-room positioning.
- [x] Public GitHub repository.
- [x] v0.1.0 release.
- [x] Wheel and source distribution assets.
- [x] CI passing.
- [x] GitHub Pages website.
- [x] README first-screen product positioning.
- [x] Chinese project introduction.
- [x] Product positioning document.
- [x] Presentation guide.
- [x] Demo workflow example.
- [x] Product Hunt listing copy.
- [x] Product Hunt final copy/paste package.
- [x] Product Hunt gallery assets.
- [x] Product Hunt thumbnail.
- [x] Promo video script.
- [x] SRT captions.
- [x] Recording/demo generation script.
- [x] Public no-key demo benchmark report.
- [x] DeepSeek failure-mode diagnosis.
- [x] Website case study page.

Still needed before a bigger launch:

- [x] Render a silent 75-second demo video draft.
- [ ] Record or add voiceover for the 60-75 second demo video.
- [ ] Upload the demo video to YouTube for Product Hunt.
- [x] Publish at least one real provider comparison after provider API keys are available.
- [x] Refresh the DeepSeek smoke result with the stable marker-based suite.
- [x] Run DeepSeek long-context and repair suites.
- [x] Diagnose DeepSeek failure modes surfaced by the benchmark set.
- [ ] Tighten DeepSeek failure modes surfaced by the benchmark set.
- [ ] Add a Product Hunt badge/link after Product Hunt is live.
- [ ] Optionally connect a custom domain.

## Launch Sequence

1. Record the demo with [video-production-kit.md](video-production-kit.md).
2. Upload the video to the launch page and social post drafts.
3. Use [launch-kit.md](launch-kit.md) for Product Hunt title, tagline, description, maker comment, and social posts.
4. Link the public demo report as the reproducible evidence artifact.
5. After launch, collect feedback into GitHub issues or the roadmap.

## Risk Notes

- The public mock benchmark proves the harness artifact flow, not real model quality.
- The DeepSeek real-provider benchmark set is a small diagnostic run, not a model leaderboard.
- Current DeepSeek results are intentionally published with failures; this is evidence that the harness can surface concrete coding-agent failure modes.
- The project should avoid claims like "better than Claude Code" or "DeepSeek V4 reversed" unless backed by clean-room, reproducible, real-provider reports.
- The safe framing is infrastructure: shared runtime, permissioned tools, traces, transcripts, reports, dashboards, and model-provider comparison workflow.

## Next Best Work

The next highest-value work is adding voiceover to the rendered demo video or tightening the DeepSeek failure modes:

```powershell
.\scripts\run-deepseek-benchmark.ps1 -SuiteSet all
```

If API keys are unavailable, the next best work is recording the demo video from the existing no-key artifacts.
