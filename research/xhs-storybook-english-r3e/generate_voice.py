#!/usr/bin/env python3
"""Generate page-aligned English narration with the user-selected Kokoro af_sol voice."""
import argparse
import hashlib
import json
import time
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx


PAGES = [
    ("The Thirsty Crow.", "口渴的小乌鸦", 0.00, 2.8),
    ("One hot day, a little crow was thirsty.", "天气很热，小乌鸦口渴了", 2.8, 4.3),
    ("Look! A jar of water!", "看！一罐水！", 7.1, 4.3),
    ("Oh no! The water was too low.", "糟糕，水太低了", 11.4, 4.3),
    ("Then it spotted some little stones.", "它发现了一些小石子", 15.7, 4.3),
    ("Plop! One stone, then another.", "扑通！一颗，又一颗", 20.0, 5.2),
    ("The water rose. It could drink!", "水升高了，终于喝到啦", 25.2, 4.3),
    ("A clever idea saves the day. Good night!", "动动脑筋，办法总会有。晚安！", 29.5, 3.8),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    model = args.model_dir
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=str(model / "model.onnx"),
                voices=str(model / "voices.bin"),
                tokens=str(model / "tokens.txt"),
                lexicon=str(model / "lexicon-us-en.txt"),
                lang="en-us",
            ),
            num_threads=2,
            provider="cpu",
        )
    )
    tts = sherpa_onnx.OfflineTts(cfg)
    assert tts.num_speakers > 1
    results = []
    for i, (en, zh, start, slot) in enumerate(PAGES):
        tick = time.monotonic()
        audio = tts.generate(en, sid=1, speed=1.0)
        x = np.asarray(audio.samples, dtype=np.float32)
        duration = len(x) / audio.sample_rate
        # Preserve a short breath before/after every line and the page-turn window.
        pad = 0.14 if i else 0.12
        if duration + pad + 0.22 > slot:
            raise RuntimeError(f"Page {i:02d}: natural voice {duration:.3f}s exceeds {slot:.3f}s slot")
        path = args.out_dir / f"page_{i:02d}_af_sol.wav"
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(audio.sample_rate)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        results.append({
            "page": i, "english": en, "chinese": zh, "page_start_s": start,
            "page_duration_s": slot, "voice_start_s": round(start + pad, 3),
            "voice_duration_s": round(duration, 3), "voice_end_s": round(start + pad + duration, 3),
            "sample_rate_hz": audio.sample_rate, "peak": float(np.max(np.abs(x))),
            "inference_s": round(time.monotonic() - tick, 3), "filename": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    (args.out_dir / "timeline.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
