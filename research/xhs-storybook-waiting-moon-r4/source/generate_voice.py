#!/usr/bin/env python3
"""Local Kokoro af_sol English lines for Waiting for the Moon."""
import argparse
import hashlib
import json
import re
import time
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

from story import LINES


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    model = a.model_dir
    original_lexicon = (model / "lexicon-us-en.txt").read_text()
    assert "weighted w ˈ A ɾ ᵻ d" in original_lexicon
    assert not re.search(r"(?m)^waited ", original_lexicon)
    # Task-local pronunciation, matching the official lexicon's 'weighted'.
    # Never edit the cached official model package.
    lexicon = a.out_dir / "lexicon-us-en-r4.txt"
    lexicon.write_text(original_lexicon.rstrip("\n") + "\nwaited w ˈ A ɾ ᵻ d\n")
    lex_words = {line.split(" ", 1)[0].lower() for line in lexicon.read_text().splitlines() if line}
    tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=str(model / "model.onnx"), voices=str(model / "voices.bin"),
                tokens=str(model / "tokens.txt"), lexicon=str(lexicon),
                lang="en-us"), num_threads=2, provider="cpu")))
    result=[]
    for i,(en,zh) in enumerate(LINES):
        tts_text=en.replace("“", "").replace("”", "")
        missing=[word for word in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?",tts_text.lower()) if word not in lex_words]
        if missing:raise RuntimeError(f"Page {i}: words missing from lexicon: {missing}")
        tick=time.monotonic()
        audio=tts.generate(tts_text,sid=1,speed=1.0)
        x=np.asarray(audio.samples,dtype=np.float32)
        f=a.out_dir/f"page_{i:02d}_af_sol.wav"
        with wave.open(str(f),"wb") as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(audio.sample_rate)
            w.writeframes((np.clip(x,-1,1)*32767).astype("<i2").tobytes())
        result.append(dict(page=i,english=en,chinese=zh,tts_input=tts_text,filename=f.name,
            duration_s=round(len(x)/audio.sample_rate,3),sample_rate_hz=audio.sample_rate,
            peak=round(float(np.max(np.abs(x))),5),
            rms=round(float(np.sqrt(np.mean(x*x))),5),
            inference_s=round(time.monotonic()-tick,3),
            sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
            task_lexicon_sha256=hashlib.sha256(lexicon.read_bytes()).hexdigest()))
    (a.out_dir/"generation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
