#!/usr/bin/env python3
"""Make only the two R3E af_sol read-aloud auditions from cached official weights."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import re
import tempfile
import time
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

HERE = Path(__file__).resolve().parent
PAGES = (3, 7)
MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_1.tar.bz2"
# The official U.S. lexicon contains "rabbit" but omits this possessive.
PATCH = "rabbit's ɹ ˈ æ b ə t s\n"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_wav(path, samples, sample_rate):
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(sample_rate)
        out.writeframes(pcm.tobytes())


def generate_without_skipped_words(tts, text):
    # sherpa-onnx writes tokenizer warnings from C++; intercept FD 2, not just
    # Python's sys.stderr, so a skipped spoken word cannot be marked ready.
    saved_stderr = os.dup(2)
    try:
        with tempfile.TemporaryFile() as diagnostic:
            os.dup2(diagnostic.fileno(), 2)
            try:
                audio = tts.generate(text, sid=1, speed=1.0)
            finally:
                os.dup2(saved_stderr, 2)
            diagnostic.seek(0)
            messages = diagnostic.read().decode("utf-8", "replace")
    finally:
        os.close(saved_stderr)
    if "OOV word skipped" in messages:
        raise RuntimeError(f"Kokoro skipped a token: {messages.strip()}")
    return audio, messages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir
    story = json.loads((HERE / "story.json").read_text())
    model = args.model_dir
    for name in ("model.onnx", "voices.bin", "tokens.txt", "lexicon-us-en.txt", "LICENSE"):
        if not (model / name).is_file():
            raise FileNotFoundError(f"Official model component unavailable: {name}")
    if sha(model / "model.onnx") != "99db0bc8fd0c5033d249fe922db16768b71b4a6b26cfd93d206fbf66c76efb5f":
        raise RuntimeError("Unexpected model.onnx SHA-256")
    if sha(model / "voices.bin") != "e64a5a581d8c2a350d848f51c3121657cd83aa07ed6109172177345874a7244c":
        raise RuntimeError("Unexpected voices.bin SHA-256")
    if sha(model / "LICENSE") != "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30":
        raise RuntimeError("Unexpected license text SHA-256")

    lexicon_source = (model / "lexicon-us-en.txt").read_text()
    if not re.search(r"(?m)^rabbit ɹ ˈ æ b ə t$", lexicon_source):
        raise RuntimeError("Official rabbit pronunciation changed; review local patch")
    if re.search(r"(?m)^rabbit's ", lexicon_source):
        raise RuntimeError("Official possessive now exists; review before applying patch")
    local_lexicon = output / "lexicon-us-en-local.txt"
    local_lexicon.write_text(lexicon_source.rstrip("\n") + "\n" + PATCH)
    (output / "lexicon_patch.txt").write_text(PATCH)
    lex_words = {line.split(" ", 1)[0].lower() for line in local_lexicon.read_text().splitlines() if line}
    config = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=str(model / "model.onnx"), voices=str(model / "voices.bin"),
            tokens=str(model / "tokens.txt"), lexicon=str(local_lexicon), lang="en-us"),
        num_threads=2, provider="cpu"))
    tts = sherpa_onnx.OfflineTts(config)
    if tts.num_speakers <= 1:
        raise RuntimeError("af_sol speaker ID 1 unavailable")
    results = []
    for page_number in PAGES:
        page = story["pages"][page_number]
        if page["page"] != page_number or page["role"] != "story":
            raise RuntimeError(f"Unexpected story mapping on page {page_number}")
        original = page["english"]
        # Kokoro's lexicon tokenizer treats opening quotes as part of "Good"
        # and can silently skip that word. Keep script punctuation unchanged.
        tts_text = original.replace("’", "'").replace("“", "").replace("”", "").replace('"', "")
        missing = [word for word in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", tts_text.lower())
                   if word not in lex_words]
        if missing:
            raise RuntimeError(f"Page {page_number}: words absent from lexicon: {missing}")
        start = time.monotonic()
        audio, tokenizer_messages = generate_without_skipped_words(tts, tts_text)
        samples = np.asarray(audio.samples, dtype=np.float32)
        if len(samples) == 0 or audio.sample_rate <= 0:
            raise RuntimeError(f"Page {page_number}: empty output")
        wav_path = output / f"page_{page_number:02d}_af_sol_audition.wav"
        save_wav(wav_path, samples, audio.sample_rate)
        active = np.flatnonzero(np.abs(samples) > .003)
        if active.size == 0:
            raise RuntimeError(f"Page {page_number}: silent output")
        duration = len(samples) / audio.sample_rate
        peak = float(np.max(np.abs(samples)))
        rms = float(np.sqrt(np.mean(samples * samples)))
        if duration < 1 or peak >= 1 or rms < .001:
            raise RuntimeError(f"Page {page_number}: invalid duration or signal level")
        results.append({
            "page": page_number, "script": original, "tts_input": tts_text,
            "emotion_brief": "gentle slight sadness" if page_number == 3 else "warm safe bedtime ending",
            "filename": wav_path.name, "sha256": sha(wav_path),
            "duration_s": round(duration, 6), "sample_rate_hz": audio.sample_rate,
            "channels": 1, "pcm_bits": 16, "peak": round(peak, 6),
            "rms": round(rms, 6), "peak_dbfs": round(20 * math.log10(peak), 3),
            "rms_dbfs": round(20 * math.log10(rms), 3),
            "leading_silence_s": round(active[0] / audio.sample_rate, 6),
            "trailing_silence_s": round((len(samples) - 1 - active[-1]) / audio.sample_rate, 6),
            "inference_s": round(time.monotonic() - start, 3),
            "tokenizer_warnings": tokenizer_messages.strip()})
    report = {
        "result": "TWO_RAW_AUDITIONS_TECHNICALLY_READY",
        "human_listening": "BLOCKED",
        "story_sha256": sha(HERE / "story.json"),
        "engine": f"sherpa-onnx {importlib.metadata.version('sherpa-onnx')}",
        "model": "kokoro-multi-lang-v1_1",
        "model_official_url": MODEL_URL, "speaker": "af_sol", "speaker_id": 1,
        "provider": "cpu", "threads": 2, "speed": 1.0,
        "weights_sha256": sha(model / "model.onnx"), "voices_sha256": sha(model / "voices.bin"),
        "license": "Apache-2.0", "license_sha256": sha(model / "LICENSE"),
        "official_lexicon_sha256": sha(model / "lexicon-us-en.txt"),
        "local_lexicon_sha256": sha(local_lexicon),
        "local_patch_sha256": sha(output / "lexicon_patch.txt"),
        "notes": "Local possessive pronunciation only; official cache unchanged. Curly apostrophe normalized and quote glyphs removed only in TTS input to prevent skipped words. No music, reverb, speed or pitch processing.",
        "clips": results}
    (output / "generation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
