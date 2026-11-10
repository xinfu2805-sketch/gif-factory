#!/usr/bin/env python3
"""Decode page and page-turn proof frames from the final MP4."""
import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
from generate_voice import PAGES


def frame(video, t, dest, size):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}",
                    "-i", str(video), "-vf", f"scale={size[0]}:{size[1]}",
                    "-frames:v", "1", str(dest)], check=True)
    return Image.open(dest).convert("RGB")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    page_times = [1.5, 4.7, 9.0, 13.0, 17.5, 22.5, 27.0, 31.0]
    sheet = Image.new("RGB", (4*360, 2*664), "white")
    draw = ImageDraw.Draw(sheet)
    for i, t in enumerate(page_times):
        im = frame(a.video, t, a.out_dir / f"page_{i:02d}.png", (360, 640))
        x, y = i%4*360, i//4*664
        sheet.paste(im, (x, y))
        draw.text((x+8, y+641), f"Page {i:02d} / {t:.1f}s", fill="#2c3d29")
    sheet.save(a.out_dir / "eight_decoded_pages.jpg", quality=90)
    turns = Image.new("RGB", (7*270, 2*505), "white")
    d = ImageDraw.Draw(turns)
    for i in range(7):
        t = PAGES[i][2] + PAGES[i][3]
        for row, moment in enumerate((t-.16, t+.08)):
            im = frame(a.video, moment, a.out_dir / f"turn_{i:02d}_{row}.png", (270, 480))
            x, y = i*270, row*505
            turns.paste(im, (x, y))
            d.text((x+6, y+482), f"{i:02d} {'before' if row == 0 else 'after'} {moment:.2f}s", fill="#2c3d29")
    turns.save(a.out_dir / "seven_page_turns.jpg", quality=88)
    frame(a.video, 1.5, a.out_dir / "cover.jpg", (1080, 1920))


if __name__ == "__main__":
    main()
