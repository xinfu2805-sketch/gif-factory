#!/usr/bin/env python3
"""Create original, restrained wind/page/star effects as a separate stem."""
import argparse
import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    timeline = json.loads((ROOT / "timeline.json").read_text())
    n = round(timeline["total_frames"] / timeline["fps"] * SR)
    rng = np.random.default_rng(20261110)
    sound = np.zeros(n, np.float32)

    # Wind: gently changing, band-limited noise, no musical notes.
    control = rng.normal(0, 1, (n // 1200) + 2).astype(np.float32)
    wind = np.interp(np.arange(n) / 1200, np.arange(len(control)), control)
    wind /= max(np.max(np.abs(wind)), 1)
    t = np.arange(n, dtype=np.float32) / SR
    sound += (0.009 + 0.003 * np.sin(2 * np.pi * .075 * t)) * wind

    # One soft paper swish at each page turn.
    for page in timeline["pages"][:-1]:
        start = round(page["end_s"] * SR)
        length = round(.43 * SR)
        noise = rng.normal(0, 1, length).astype(np.float32)
        smooth = np.convolve(noise, np.ones(80, np.float32) / 80, mode="same")
        envelope = np.sin(np.linspace(0, np.pi, length, dtype=np.float32)) ** 2
        sound[start:start + length] += .019 * smooth * envelope

    # Small glassy star ticks, deliberately sparse and kept behind speech.
    for sec in (11.75, 12.4, 13.1, 13.75, 14.4, 25.3):
        start = round(sec * SR)
        length = round(.52 * SR)
        tt = np.arange(length, dtype=np.float32) / SR
        bell = (np.sin(2 * np.pi * 1046.5 * tt) +
                .28 * np.sin(2 * np.pi * 2093 * tt)) * np.exp(-9 * tt)
        sound[start:start + length] += .0032 * bell

    sound = np.clip(sound, -.9, .9)
    stereo = np.column_stack((sound, sound * .97))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(args.output), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SR)
        out.writeframes((stereo * 32767).astype("<i2").tobytes())
    print(f"{args.output}: {len(sound) / SR:.3f}s, peak {np.max(np.abs(sound)):.4f}")


if __name__ == "__main__":
    main()
