#!/usr/bin/env python3
"""Timeline alignment and adaptive music ducking; keeps all stems independent."""
import argparse
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000


def decode(path):
    run = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                          "-f", "f32le", "-ar", str(SR), "-ac", "2", "-"],
                         check=True, capture_output=True)
    return np.frombuffer(run.stdout, dtype="<f4").reshape(-1, 2).copy()


def save(path, samples):
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SR)
        out.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())


def fit(samples, n):
    if len(samples) >= n:
        return samples[:n].copy()
    return np.pad(samples, ((0, n - len(samples)), (0, 0)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--music", type=Path, required=True)
    parser.add_argument("--foley", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    timeline = json.loads((ROOT / "timeline.json").read_text())
    n = round(timeline["total_frames"] / timeline["fps"] * SR)
    voice = np.zeros((n, 2), np.float32)
    for page in timeline["pages"]:
        clip = decode(ROOT / "voice" / page["voice_file"])
        start = round(page["voice_start_s"] * SR)
        end = start + len(clip)
        if end > n or end / SR > page["end_s"] - .2:
            raise ValueError(f"Voice crosses page boundary: {page['page']}")
        voice[start:end] += clip
    voice *= 1.15
    music = fit(decode(args.music), n)
    foley = fit(decode(args.foley), n)
    hop = round(.02 * SR)
    blocks = (n + hop - 1) // hop
    gains = np.empty(blocks, np.float32)
    gain = .70
    for i in range(blocks):
        part = voice[i * hop:(i + 1) * hop]
        speaking = np.sqrt(np.mean(part ** 2)) > .005 if len(part) else False
        target, tau = (.25, .11) if speaking else (.70, .65)
        gain += (target - gain) * (1 - np.exp(-.02 / tau))
        gains[i] = gain
    curve = np.interp(np.arange(n) / hop, np.arange(blocks), gains)
    ducked = music * curve[:, None]
    mixed = voice + ducked + foley
    limiter = min(1., .95 / max(float(np.max(np.abs(mixed))), 1e-9))
    mixed *= limiter
    stems = {"narration_aligned.wav": voice, "lullaby_ducked.wav": ducked,
             "foley_separate.wav": foley, "mix.wav": mixed}
    for name, samples in stems.items():
        save(args.output_dir / name, samples)
    report = {"duration_s": n / SR, "sample_rate_hz": SR, "channels": 2,
              "music_source": str(args.music), "foley_source": str(args.foley),
              "music_gain_during_voice_target": .25,
              "music_gain_between_voice_target": .70,
              "pre_limiter_peak": float(np.max(np.abs(voice + ducked + foley))),
              "limiter_gain": limiter,
              "stems": {name: {"rms": float(np.sqrt(np.mean(samples ** 2))),
                                "peak": float(np.max(np.abs(samples))),
                                "sha256": hashlib.sha256((args.output_dir / name).read_bytes()).hexdigest()}
                        for name, samples in stems.items()}}
    (args.output_dir / "audio_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
