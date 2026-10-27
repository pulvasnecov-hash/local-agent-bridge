#!/usr/bin/env python3
"""Render the verified offline transcript. Optional dev tools: Pillow and FFmpeg."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (1100, 680)


def font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts") / ("consolab.ttf" if bold else "consola.ttf"),
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def scene(title, command, output, number):
    canvas = Image.new("RGB", SIZE, "#09111f")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((26, 25, 1074, 655), radius=22, fill="#111d31", outline="#29405b", width=2)
    draw.text((52, 45), "LOCAL AGENT BRIDGE", font=font(34, True), fill="#7dd3fc")
    draw.text((52, 94), "MIT / unlimited bridge launches / Python", font=font(21), fill="#b9c8dc")
    draw.text((52, 150), title, font=font(28, True), fill="white")
    draw.rounded_rectangle((48, 200, 1052, 562), radius=12, fill="#080e18")
    lines = []
    for line in ("$ " + command + "\n\n" + output).splitlines():
        lines.extend(textwrap.wrap(line, width=70, replace_whitespace=False, drop_whitespace=False) or [""])
    for index, line in enumerate(lines[:12]):
        draw.text((68, 219 + index * 26), line, font=font(20), fill="#a7f3d0" if index < 2 else "#d6e2f1")
    draw.text((52, 587), "OFFLINE DEMO: Python test executor. No LLM calls.", font=font(19, True), fill="#fbbf24")
    draw.text((52, 617), "Replayed real CLI output; pacing edited for readability.", font=font(17), fill="#9cb0c8")
    draw.text((992, 617), f"{number}/6", font=font(18), fill="#9cb0c8")
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=ROOT / "assets")
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    args.assets.mkdir(parents=True, exist_ok=True)
    args.dist.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable, str(ROOT / "examples/offline_demo.py"), "--json"],
                            capture_output=True, text=True, encoding="utf-8", timeout=45, check=True)
    report = json.loads(result.stdout)
    (args.dist / "demo-transcript.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    chapters = [
        ("Task handoff you can reproduce", "python examples/offline_demo.py",
         "A task file goes through the real bridge.\nA local Python fixture creates an artifact.\nThe artifact and journal are checked separately.\n\nThis demo tests transport, not model reasoning.", 6),
        *[(step["title"], step["command"], step["output"], duration)
          for step, duration in zip(report["steps"], (6, 9, 7, 8))],
        ("Try it on your computer", "git clone <repository URL below>",
         "github.com/pulvasnecov-hash/local-agent-bridge\n\nWindows + Linux / Python 3.10+ / MIT\nModel and AI-client limits still apply.\n\nShare installation feedback in GitHub Issues.", 6),
    ]
    frames = [scene(title, command, output, index + 1) for index, (title, command, output, _) in enumerate(chapters)]
    frames[0].save(args.assets / "demo-poster.png", optimize=True)
    palette_frames = [frame.resize((880, 544)).quantize(colors=64) for frame in frames]
    palette_frames[0].save(args.assets / "demo.gif", save_all=True, append_images=palette_frames[1:],
                           duration=[c[3] * 1000 for c in chapters], loop=0, optimize=True, disposal=2)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required for MP4 export")
    with tempfile.TemporaryDirectory(prefix="lab-demo-frames-") as temporary:
        folder = Path(temporary).resolve()
        manifest = []
        for index, (frame, chapter) in enumerate(zip(frames, chapters)):
            frame.save(folder / f"scene-{index}.png")
            manifest += [f"file 'scene-{index}.png'", f"duration {chapter[3]}"]
        manifest.append(f"file 'scene-{len(frames) - 1}.png'")
        (folder / "frames.txt").write_text("\n".join(manifest), encoding="utf-8")
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "1",
                        "-i", "frames.txt", "-vf", "fps=24", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", "-t", str(sum(chapter[3] for chapter in chapters)),
                        str((args.dist / "local-agent-bridge-demo.mp4").resolve())],
                       cwd=folder, check=True, timeout=90)
    print(json.dumps({"duration_seconds": sum(c[3] for c in chapters), "verified_result": report["verified_result"],
                      "gif_bytes": (args.assets / "demo.gif").stat().st_size,
                      "mp4_bytes": (args.dist / "local-agent-bridge-demo.mp4").stat().st_size}))


if __name__ == "__main__":
    main()
