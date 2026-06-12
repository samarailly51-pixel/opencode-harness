"""Render a silent captioned demo video for OpenCode Harness.

This script is intentionally optional and keeps video dependencies out of the
runtime package. Install the renderer dependencies when needed:

    python -m pip install imageio imageio-ffmpeg pillow

Then run:

    python scripts/render-demo-video.py
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    import imageio.v2 as imageio
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - optional production helper
    raise SystemExit(
        "Missing optional video dependencies. Install with: "
        "python -m pip install imageio imageio-ffmpeg pillow"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
W, H = 1920, 1080
FPS = 24

INK = (24, 32, 29)
MUTED = (82, 97, 92)
PAPER = (247, 249, 246)
GREEN = (31, 122, 87)
TEAL = (15, 118, 110)
BLUE = (36, 87, 166)
GOLD = (183, 121, 31)
LINE = (220, 227, 221)
WHITE = (255, 255, 255)
DARK = (21, 35, 29)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    if not path.exists():
        path = Path("C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size)


F_TITLE = font(78, True)
F_H2 = font(52, True)
F_BODY = font(34)
F_BODY_BOLD = font(34, True)
F_SMALL = font(24)
F_MONO = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 25) if Path("C:/Windows/Fonts/consola.ttf").exists() else font(25)


def rounded(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def fit_cover(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    sw, sh = size
    scale = max(sw / img.width, sh / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - sw) // 2
    y = (nh - sh) // 2
    return img.crop((x, y, x + sw, y + sh))


def fit_contain(path: Path, size: tuple[int, int], fill=WHITE) -> Image.Image:
    img = Image.open(path).convert("RGB")
    sw, sh = size
    scale = min(sw / img.width, sh / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, fill)
    canvas.paste(resized, ((sw - nw) // 2, (sh - nh) // 2))
    return canvas


def wrap(draw: ImageDraw.ImageDraw, text: str, max_width: int, fnt: ImageFont.FreeTypeFont) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, max_width: int, fnt, fill, line_gap: int = 10) -> int:
    x, y = xy
    for line in wrap(draw, text, max_width, fnt):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y


def base() -> Image.Image:
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(PAPER[0] + (232 - PAPER[0]) * y / H)
        g = int(PAPER[1] + (243 - PAPER[1]) * y / H)
        b = int(PAPER[2] + (240 - PAPER[2]) * y / H)
        draw.line((0, y, W, y), fill=(r, g, b))
    return img


def brand(draw: ImageDraw.ImageDraw, dark: bool = False) -> None:
    fill = WHITE if dark else GREEN
    text_fill = WHITE if dark else INK
    rounded(draw, (96, 72, 176, 124), 14, fill)
    draw.text((120, 80), "OH", font=font(29, True), fill=GREEN if dark else WHITE)
    draw.text((198, 81), "OpenCode Harness", font=font(31, True), fill=text_fill)


def caption_bar(img: Image.Image, text: str) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((190, 900, W - 190, 1012), radius=28, fill=(10, 20, 16, 225))
    lines = wrap(draw, text, W - 480, font(30, True))
    y = 924 if len(lines) == 1 else 912
    for line in lines[:2]:
        tw = draw.textlength(line, font=font(30, True))
        draw.text(((W - tw) / 2, y), line, font=font(30, True), fill=WHITE)
        y += 40
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))


def add_progress(draw: ImageDraw.ImageDraw, scene_i: int, total: int = 6) -> None:
    x0, y0, w, gap = 96, 1018, 128, 14
    for i in range(total):
        color = GREEN if i <= scene_i else (205, 216, 209)
        rounded(draw, (x0 + i * (w + gap), y0, x0 + i * (w + gap) + w, y0 + 10), 5, color)


def problem_scene(t: float, caption: str) -> Image.Image:
    img = base()
    draw = ImageDraw.Draw(img)
    brand(draw)
    draw.text((96, 205), "Coding agents are easy to demo.", font=F_TITLE, fill=INK)
    draw.text((96, 298), "Hard to compare.", font=F_TITLE, fill=GREEN)
    providers = ["DeepSeek", "Qwen", "Claude", "OpenAI", "Local Models"]
    for i, name in enumerate(providers):
        x = 114 + i * 330
        y = 460 + int(math.sin(t * 2.5 + i) * 12)
        rounded(draw, (x, y, x + 252, y + 84), 18, WHITE, LINE, 2)
        draw.ellipse((x + 24, y + 31, x + 45, y + 52), fill=[GREEN, TEAL, GOLD, BLUE, INK][i])
        draw.text((x + 62, y + 22), name, font=F_BODY_BOLD, fill=INK)
    draw.text((120, 650), "Different prompts", font=F_H2, fill=MUTED)
    draw.text((670, 650), "Different tools", font=F_H2, fill=MUTED)
    draw.text((1160, 650), "Different traces", font=F_H2, fill=MUTED)
    caption_bar(img, caption)
    add_progress(draw, 0)
    return img


def reveal_scene(t: float, caption: str) -> Image.Image:
    img = base()
    draw = ImageDraw.Draw(img)
    brand(draw)
    draw.text((96, 178), "One shared runtime", font=F_TITLE, fill=INK)
    draw.text((96, 270), "for coding-agent evals.", font=F_TITLE, fill=GREEN)
    labels = ["task", "model", "tools", "trace", "report"]
    x0, y = 170, 506
    for i, label in enumerate(labels):
        x = x0 + i * 325
        rounded(draw, (x, y, x + 210, y + 110), 22, WHITE, LINE, 2)
        draw.text((x + 52, y + 34), label, font=F_BODY_BOLD, fill=INK)
        if i < len(labels) - 1:
            draw.line((x + 220, y + 55, x + 300, y + 55), fill=GREEN, width=8)
            draw.polygon([(x + 300, y + 55), (x + 276, y + 40), (x + 276, y + 70)], fill=GREEN)
    command = "python -m opencode_harness eval examples/mock-suite.json --preset mock"
    rounded(draw, (180, 710, W - 180, 798), 18, DARK)
    draw.text((226, 738), command, font=F_MONO, fill=(217, 244, 232))
    caption_bar(img, caption)
    add_progress(draw, 1)
    return img


def runtime_scene(t: float, caption: str) -> Image.Image:
    img = base()
    draw = ImageDraw.Draw(img)
    brand(draw)
    draw.text((96, 168), "Model-neutral by design", font=F_TITLE, fill=INK)
    draw.text((100, 265), "Swap providers. Keep the workflow.", font=F_H2, fill=MUTED)
    providers = [
        ("DeepSeek", GREEN), ("Qwen", TEAL), ("Claude", GOLD), ("OpenAI", BLUE),
        ("vLLM", GREEN), ("SGLang", TEAL), ("Ollama", GOLD), ("Local", INK)
    ]
    for i, (name, color) in enumerate(providers):
        row, col = divmod(i, 4)
        x = 128 + col * 430
        y = 420 + row * 142
        rounded(draw, (x, y, x + 320, y + 92), 18, WHITE, LINE, 2)
        draw.ellipse((x + 32, y + 34, x + 56, y + 58), fill=color)
        draw.text((x + 78, y + 24), name, font=F_BODY_BOLD, fill=INK)
    caption_bar(img, caption)
    add_progress(draw, 2)
    return img


def tools_scene(t: float, caption: str) -> Image.Image:
    img = base()
    draw = ImageDraw.Draw(img)
    brand(draw)
    draw.text((96, 160), "Permissioned tools", font=F_TITLE, fill=INK)
    draw.text((96, 250), "plus MCP-compatible extension points.", font=F_H2, fill=GREEN)
    tools = ["read_file", "search_files", "apply_patch", "shell", "repo_map", "context_pack", "todo_set", "finish"]
    for i, name in enumerate(tools):
        row, col = divmod(i, 4)
        x = 120 + col * 420
        y = 400 + row * 118
        rounded(draw, (x, y, x + 340, y + 72), 14, WHITE, LINE, 2)
        draw.text((x + 32, y + 18), name, font=F_BODY_BOLD, fill=INK)
    rounded(draw, (430, 705, W - 430, 805), 22, DARK)
    draw.text((505, 734), "MCP tools / resources / prompts / diagnostics / approvals", font=F_BODY_BOLD, fill=(217, 244, 232))
    caption_bar(img, caption)
    add_progress(draw, 3)
    return img


def eval_scene(t: float, caption: str) -> Image.Image:
    img = base()
    draw = ImageDraw.Draw(img)
    brand(draw)
    draw.text((96, 122), "Traceable eval outputs", font=F_TITLE, fill=INK)
    left = fit_contain(ROOT / "site/assets/trace-preview.png", (760, 488), fill=WHITE)
    right = fit_contain(ROOT / "site/assets/dashboard-preview.png", (760, 488), fill=WHITE)
    for x, panel in [(112, left), (1048, right)]:
        shadow = Image.new("RGBA", (760, 488), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle((0, 0, 760, 488), radius=18, fill=(0, 0, 0, 30))
        img.paste(shadow.convert("RGB"), (x + 16, 302 + 16))
        img.paste(panel, (x, 302))
        draw.rounded_rectangle((x, 302, x + 760, 790), radius=18, outline=LINE, width=2)
    caption_bar(img, caption)
    add_progress(draw, 4)
    return img


def cta_scene(t: float, caption: str) -> Image.Image:
    img = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)
    brand(draw, dark=True)
    draw.text((96, 210), "OpenCode Harness v0.1.0", font=F_TITLE, fill=WHITE)
    draw.text((100, 310), "Open source now.", font=F_TITLE, fill=(159, 224, 195))
    links = [
        "Website: samarailly51-pixel.github.io/opencode-harness",
        "GitHub: github.com/samarailly51-pixel/opencode-harness",
        "Release: v0.1.0",
        "Demo report: benchmarks/v0.1-mock-smoke",
    ]
    y = 470
    for line in links:
        draw.text((140, y), line, font=F_BODY_BOLD, fill=(226, 238, 232))
        y += 70
    rounded(draw, (126, 780, 1000, 860), 22, GREEN)
    draw.text((170, 800), "Run the same coding-agent workflow everywhere.", font=F_BODY_BOLD, fill=WHITE)
    caption_bar(img, caption)
    add_progress(draw, 5)
    return img


SCENES = [
    (8, problem_scene, "Coding agents are everywhere, but comparing them is messy."),
    (10, reveal_scene, "One agent loop, one tool layer, one trace format, one eval surface."),
    (16, runtime_scene, "Run the same workflow across hosted and local model providers."),
    (16, tools_scene, "Permissioned tools and MCP extension points make runs inspectable."),
    (14, eval_scene, "Every run produces traces, transcripts, reports, and dashboards."),
    (11, cta_scene, "OpenCode Harness v0.1.0 is open source now."),
]


def render(output: Path, thumbnail: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    total_frames = sum(duration for duration, _, _ in SCENES) * FPS
    frame_count = 0
    with imageio.get_writer(
        output,
        fps=FPS,
        codec="libx264",
        quality=7,
        macro_block_size=1,
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    ) as writer:
        for duration, scene_fn, caption in SCENES:
            frames = duration * FPS
            for i in range(frames):
                t = i / max(frames - 1, 1)
                frame = scene_fn(t, caption)
                writer.append_data(np.asarray(frame))
                if frame_count == 0:
                    thumbnail.parent.mkdir(parents=True, exist_ok=True)
                    frame.save(thumbnail)
                frame_count += 1
                if frame_count % (FPS * 10) == 0:
                    print(f"Rendered {frame_count}/{total_frames} frames")
    print(f"Wrote {output}")
    print(f"Wrote {thumbnail}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render OpenCode Harness demo video")
    parser.add_argument("--output", default="media/demo-video/opencode-harness-demo.mp4")
    parser.add_argument("--thumbnail", default="media/demo-video/opencode-harness-demo-thumbnail.png")
    args = parser.parse_args()
    render(ROOT / args.output, ROOT / args.thumbnail)


if __name__ == "__main__":
    main()
