# Demo Video

This directory contains the rendered OpenCode Harness demo video artifacts.

Generated files:

- `opencode-harness-demo.mp4`
- `opencode-harness-demo-thumbnail.png`
- `opencode-harness-demo-contact-sheet.png`

Render locally:

```powershell
python -m pip install imageio imageio-ffmpeg pillow
python scripts/render-demo-video.py
```

The video is a silent, captioned 75-second product demo built from repository assets. Use the contact sheet to review key frames quickly. The voiceover script and SRT captions live in:

- [../../docs/promo-video-script.md](../../docs/promo-video-script.md)
- [../../docs/video-captions.srt](../../docs/video-captions.srt)
- [../../docs/video-production-kit.md](../../docs/video-production-kit.md)
