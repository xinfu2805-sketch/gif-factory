#!/usr/bin/env python3
"""Align 8 voice clips and duck the existing independent R2 lullaby underneath speech."""
import argparse
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 48000
TOTAL = 33.3
N = int(SR * TOTAL)


def decode(path, channels=2):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ar", str(SR),
                        "-ac", str(channels), "-"], check=True, capture_output=True)
    a = np.frombuffer(p.stdout, dtype="<f4")
    return a.reshape(-1, channels).copy()


def save(path, x):
    x = np.asarray(x, np.float32)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def fit(a):
    if len(a) < N:
        return np.pad(a, ((0, N-len(a)), (0, 0)))
    return a[:N].copy()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--voice-dir", type=Path, required=True)
    p.add_argument("--music", type=Path, required=True)
    p.add_argument("--foley", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    timeline = json.loads((a.voice_dir / "timeline.json").read_text())
    voice = np.zeros((N, 2), np.float32)
    for page in timeline:
        clip = decode(a.voice_dir / page["filename"])
        start = int(round(page["voice_start_s"] * SR))
        end = start + len(clip)
        if end > N or end/SR > page["page_start_s"]+page["page_duration_s"]-0.22:
            raise RuntimeError(f"Voice crosses page boundary: {page['page']}")
        voice[start:end] += clip
    voice *= 1.24
    music = fit(decode(a.music))
    foley = fit(decode(a.foley))
    # Speech activity is measured in 20 ms blocks; fast attack and gentle release.
    hop = int(SR * .02)
    nblocks = int(np.ceil(N / hop))
    active = np.zeros(nblocks, np.float32)
    for k in range(nblocks):
        v = voice[k*hop:(k+1)*hop]
        active[k] = float(np.sqrt(np.mean(v*v))) > .006 if len(v) else False
    gain = np.empty(nblocks, np.float32)
    g = 1.0
    for k, on in enumerate(active):
        target = .30 if on else .82
        tau = .11 if on else .68
        g += (target-g) * (1-np.exp(-.02/tau))
        gain[k] = g
    per_sample = np.interp(np.arange(N, dtype=np.float32)/hop,
                           np.arange(nblocks, dtype=np.float32), gain).astype(np.float32)
    ducked_music = music * per_sample[:, None]
    foley *= .74
    mix = voice + ducked_music + foley
    peak = float(np.max(np.abs(mix)))
    limiter = min(1, .94 / peak)
    mix *= limiter
    save(a.out_dir / "narration_aligned.wav", voice)
    save(a.out_dir / "lullaby_ducked.wav", ducked_music)
    save(a.out_dir / "foley_separate.wav", foley)
    save(a.out_dir / "final_mix.wav", mix)
    report = {"sample_rate_hz": SR, "channels": 2, "duration_s": TOTAL,
              "voice_rms": float(np.sqrt(np.mean(voice**2))),
              "music_rms": float(np.sqrt(np.mean(ducked_music**2))),
              "foley_rms": float(np.sqrt(np.mean(foley**2))),
              "mix_rms": float(np.sqrt(np.mean(mix**2))), "mix_peak": float(np.max(np.abs(mix))),
              "pre_limiter_peak": peak, "limiter_gain": limiter,
              "music_gain_during_voice_target": .30, "music_gain_between_voice_target": .82,
              "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(a.out_dir.glob("*.wav"))}}
    (a.out_dir / "audio_report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
