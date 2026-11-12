#!/usr/bin/env python3
"""Export one-shot page action GIFs from already drawn frames; not a pose generator."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageSequence


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_box(raw):
    try:
        box = tuple(int(x.strip()) for x in raw.split(","))
        if len(box) != 4 or box[0] < 0 or box[1] < 0 or box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError()
        return box
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected left,top,right,bottom") from exc


def changed_area(first, second, box):
    diff = ImageChops.difference(first.crop(box).convert("RGB"), second.crop(box).convert("RGB")).convert("L")
    counts = diff.histogram()
    return sum(counts[17:]) / max(1, sum(counts))


def export(frames_dir, output, subject_box, frame_ms=180, last_hold_ms=800):
    paths = sorted(Path(frames_dir).glob("*.png"))
    if len(paths) < 3:
        raise ValueError("at least three consecutive real pose frames are required")
    frames = [Image.open(p).convert("RGB") for p in paths]
    width, height = frames[0].size
    if any(im.size != (width, height) for im in frames):
        raise ValueError("all frames must have one fixed canvas")
    left, top, right, bottom = subject_box
    if right > width or bottom > height:
        raise ValueError("subject box outside canvas")
    if any(ms < 20 or ms % 10 for ms in (frame_ms, last_hold_ms)):
        raise ValueError("GIF frame durations must be >=20ms and multiples of 10ms")
    changes = [changed_area(frames[i], frames[i + 1], subject_box) for i in range(len(frames) - 1)]
    start_to_end = changed_area(frames[0], frames[-1], subject_box)
    if start_to_end < .008 or sum(x > .004 for x in changes) < 2:
        raise ValueError("static character: background movement cannot substitute for character action")
    # Share one palette, canvas and character coordinate frame across every frame.
    sample = Image.new("RGB", (3 * width, height))
    for i, frame in enumerate((frames[0], frames[len(frames) // 2], frames[-1])):
        sample.paste(frame, (i * width, 0))
    palette = sample.quantize(colors=192)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    duration = [frame_ms] * len(indexed)
    duration[-1] = last_hold_ms
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Omit 'loop': one story action plays once and holds its final pose.
    indexed[0].save(output, save_all=True, append_images=indexed[1:],
                    duration=duration, disposal=1, optimize=False)
    with Image.open(output) as actual:
        decoded = sum(1 for _ in ImageSequence.Iterator(actual))
        if decoded != len(paths) or "loop" in actual.info:
            raise RuntimeError("GIF frame count or one-shot playback invariant failed")
    review = {
        "contract": "GIF-FIRST-ACTION-R1",
        "sources": [{"path": p.name, "sha256": digest(p)} for p in paths],
        "output_sha256": digest(output),
        "size": [width, height], "frames": decoded, "durations_ms": duration,
        "subject_box": subject_box, "start_end_changed_ratio": round(start_to_end, 5),
        "consecutive_changed_ratios": [round(v, 5) for v in changes],
        "TECHNICAL_GIF_PASS": "PASS",
        "ACTION_PASS": "BLOCKED_PENDING_HUMAN_VISUAL_REVIEW",
        "warning": "Changed pixels do not prove anatomy, identity, contact or emotional acting."
    }
    output.with_suffix(".qa.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return review


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames_dir", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--subject-box", type=parse_box, required=True)
    ap.add_argument("--frame-ms", type=int, default=180)
    ap.add_argument("--last-hold-ms", type=int, default=800)
    args = ap.parse_args()
    result = export(args.frames_dir, args.output, args.subject_box, args.frame_ms, args.last_hold_ms)
    print(json.dumps({"frames": result["frames"], "TECHNICAL_GIF_PASS": result["TECHNICAL_GIF_PASS"],
                      "ACTION_PASS": result["ACTION_PASS"]}))


if __name__ == "__main__":
    main()
