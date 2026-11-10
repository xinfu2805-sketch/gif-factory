#!/usr/bin/env python3
"""Objective media checks only. Never signs artistic or release quality."""
import argparse
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np


def probe(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration,size:stream=index,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def wav_stats(path):
    with wave.open(str(path), "rb") as w:
        sr, ch, count = w.getframerate(), w.getnchannels(), w.getnframes()
        a = np.frombuffer(w.readframes(count), dtype="<i2").astype(np.float32) / 32768
    return {"duration_s": round(count/sr, 3), "sample_rate_hz": sr, "channels": ch,
            "rms": round(float(np.sqrt(np.mean(a*a))), 6),
            "peak": round(float(np.max(np.abs(a))), 6),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    video = a.output / "The_Thirsty_Crow_bilingual_1080x1920.mp4"
    data = probe(video)
    v = next(x for x in data["streams"] if x["codec_name"] == "h264")
    au = next(x for x in data["streams"] if x["codec_name"] == "aac")
    checks = {
        "video_1080x1920": (v["width"], v["height"]) == (1080, 1920),
        "encoded_24fps_from_R2_12fps_picture": v["r_frame_rate"] == "24/1",
        "799_frames": int(v["nb_frames"]) == 799,
        "duration_33_3s": abs(float(data["format"]["duration"])-33.3)<.03,
        "aac_48k_stereo": au["sample_rate"] == "48000" and au["channels"] == 2,
    }
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"],
                   capture_output=True, check=True)
    checks["full_video_and_audio_decode"] = True
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-f", "f32le",
                          "-ac", "2", "-ar", "48000", "-"], capture_output=True, check=True).stdout
    aac = np.frombuffer(pcm, dtype="<f4")
    aac_rms = float(np.sqrt(np.mean(aac*aac)))
    checks["final_aac_nonblank"] = aac_rms > .005
    timeline = json.loads((a.output / "voice/timeline.json").read_text())
    checks["8_voice_lines"] = len(timeline) == 8
    checks["no_voice_crosses_page_turn"] = all(
        x["voice_end_s"] <= x["page_start_s"]+x["page_duration_s"]-.22 for x in timeline)
    clips = {x["filename"]: wav_stats(a.output / "voice" / x["filename"]) for x in timeline}
    checks["voice_clips_nonblank"] = all(x["rms"]>.005 and x["peak"]<.98 for x in clips.values())
    stems = {x: wav_stats(a.output / "audio" / x) for x in
             ("narration_aligned.wav", "lullaby_ducked.wav", "foley_separate.wav", "final_mix.wav")}
    checks["all_stems_33_3s_and_nonblank"] = all(
        abs(s["duration_s"]-33.3)<.01 and s["rms"]>.0005 for s in stems.values())
    report = {"technical_checks": checks, "video_probe": data, "final_aac_rms": aac_rms,
              "video_sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
              "voice_clips": clips, "audio_stems": stems,
              "note": "Decoding and signal checks cannot certify pronunciation, acting, music quality, rights, or crow joint animation."}
    a.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(checks, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
