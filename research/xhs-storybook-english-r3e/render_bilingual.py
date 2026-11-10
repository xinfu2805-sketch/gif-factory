#!/usr/bin/env python3
"""Replace printed Chinese lower-page copy with clean bilingual captions.

Uses the accepted R2 video as picture input; never regenerates or moves the crow.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from generate_voice import PAGES


ART = ["00_封面.webp", "01_故事第1页.webp", "02_故事第2页.webp", "03_故事第3页.webp",
       "04_故事第4页.webp", "05_故事第5页.webp", "06_故事第6页.webp", "07_故事启发.webp"]
START = [v[2] for v in PAGES]
W, H, FPS = 1080, 1920, 24
GREEN = (57, 72, 49, 255)


def paper_patches(art_dir, out_dir):
    out = []
    for i, name in enumerate(ART):
        im = Image.open(art_dir / name).convert("RGB")
        bbox = (100, 0, 980, 1440) if i in (0, 7) else (120, 0, 960, 1440)
        a = np.asarray(im.crop(bbox).resize((720, 1280), Image.Resampling.LANCZOS))
        if i == 0:
            x0, y0, x1, y1 = 135, 1090, 635, 1280
            caption_y = 1710
        elif i == 7:
            x0, y0, x1, y1 = 130, 930, 640, 1240
            caption_y = 1450
        else:
            x0, y0, x1, y1 = 115, 810, 645, 1160
            caption_y = 1280
        # Rebuild just the blank printed-paper region from a clean strip of the
        # same page. Ink-pixel inpainting left pale Chinese glyph shadows.
        strip_y = 1245 if i in (0, 7) else 1180
        strip = a[strip_y:strip_y+26, x0:x1].copy()
        if strip.shape[0] != 26:
            raise RuntimeError("No clean paper strip")
        target_h = y1-y0
        sheet = np.concatenate([strip if j % 2 == 0 else strip[::-1]
                                for j in range((target_h+25)//26)], axis=0)[:target_h]
        clean = a.copy()
        clean[y0:y1, x0:x1] = sheet
        clean = cv2.resize(clean, (W, H), interpolation=cv2.INTER_LANCZOS4)
        yy0, yy1 = int(y0 * 1.5), int(y1 * 1.5)
        xx0, xx1 = int(x0 * 1.5), int(x1 * 1.5)
        # Blend a narrow edge so the still paper joins the decoded moving frame.
        alpha = np.zeros((H, W), np.float32)
        alpha[yy0:yy1, xx0:xx1] = 1
        if i != 0:
            alpha = cv2.GaussianBlur(alpha, (0, 0), 30 if i == 7 else 16)
        layer = Image.new("RGBA", (W, H))
        draw = ImageDraw.Draw(layer)
        en, zh, _, _ = PAGES[i]
        en_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", 56 if len(en) < 39 else 50)
        zh_font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 41)
        # Single line wherever possible; deliberate two-line breaks for the longest lines.
        english = en if draw.textlength(en, font=en_font) < 875 else en.replace(" crow was ", " crow\nwas ").replace(" saves the day. ", " saves the day.\n")
        lines = english.split("\n")
        for j, line in enumerate(lines):
            box = draw.textbbox((0, 0), line, font=en_font)
            width = box[2] - box[0]
            draw.text(((W-width)/2, caption_y+j*70), line, font=en_font, fill=GREEN,
                      stroke_width=0)
        cy = caption_y + len(lines)*76 + 18
        box = draw.textbbox((0, 0), zh, font=zh_font)
        width = box[2] - box[0]
        draw.text(((W-width)/2, cy), zh, font=zh_font, fill=(80, 90, 69, 255))
        patch = {"clean": clean, "alpha": alpha, "caption": np.asarray(layer),
                 "ink_box": [xx0, yy0, xx1, yy1]}
        Image.fromarray(clean).save(out_dir / f"clean_page_{i:02d}.png")
        layer.save(out_dir / f"caption_page_{i:02d}.png")
        out.append(patch)
    return out


def apply(frame, patch, lo=0, hi=W, caption_opacity=1.0):
    x0, y0, x1, y1 = patch["ink_box"]
    x0, x1 = max(x0, lo), min(x1, hi)
    if x1 > x0:
        a = patch["alpha"][y0:y1, x0:x1, None]
        frame[y0:y1, x0:x1] = (frame[y0:y1, x0:x1] * (1-a) + patch["clean"][y0:y1, x0:x1] * a).astype(np.uint8)
    cap = patch["caption"]
    # Caption alpha is entirely zero outside letters; apply inside the page-wipe slice.
    ya, yb = 1180, H
    if caption_opacity > 0:
        a = cap[ya:yb, lo:hi, 3:4].astype(np.float32) / 255.0 * caption_opacity
        frame[ya:yb, lo:hi] = (frame[ya:yb, lo:hi]*(1-a) + cap[ya:yb, lo:hi, :3]*a).astype(np.uint8)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-video", type=Path, required=True)
    p.add_argument("--artwork-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    patches = paper_patches(a.artwork_dir, a.out_dir)
    cap = cv2.VideoCapture(str(a.base_video))
    if not cap.isOpened() or abs(cap.get(cv2.CAP_PROP_FPS)-FPS)>0.01:
        raise RuntimeError("R2 source video not readable at expected 24 fps")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast",
           "-crf", "18", "-pix_fmt", "yuv420p", str(a.out_dir / "bilingual_picture.mp4")]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    k = 0
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        if bgr.shape != (H, W, 3):
            raise RuntimeError("R2 frame size changed")
        # R2 picture was composed at 12 fps and duplicated to 24 fps. Its page
        # seam follows the source-frame clock, not the 24 fps output PTS.
        now = (k // 2) / 12
        i = max(j for j, start in enumerate(START) if start <= now)
        t = now - START[i]
        frame = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if i < 7 and t > PAGES[i][3]-0.28:
            v = (t-(PAGES[i][3]-0.28))/0.28
            seam = int(W*(1-v))
            # Printed copy is cleaned on both halves, but neither page's new
            # subtitle is sliced through the paper seam.
            apply(frame, patches[i], 0, max(0,seam), 0)
            apply(frame, patches[i+1], min(W,seam), W, 0)
        else:
            fade_in = min(1.0, t/.35)
            fade_out = 1.0 if i == 7 else min(1.0, max(0.0, (PAGES[i][3]-.28-t)/.27))
            apply(frame, patches[i], caption_opacity=min(fade_in, fade_out))
        enc.stdin.write(frame.tobytes())
        k += 1
    cap.release()
    enc.stdin.close()
    err = enc.stderr.read().decode("utf-8", "replace")
    if enc.wait() or k != 799:
        raise RuntimeError(f"Render failed: {k} frames; {err[-1000:]}")
    (a.out_dir / "picture_frames.json").write_text(json.dumps({"frames":k,"fps":FPS,"width":W,"height":H},indent=2)+"\n")
    print(f"Rendered {k} bilingual frames")


if __name__ == "__main__":
    main()
