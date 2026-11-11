#!/usr/bin/env python3
"""Objective media verification; subjective quality gates remain separate."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd):
    return subprocess.run(cmd, capture_output=True, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    timeline = json.loads((ROOT / "timeline.json").read_text())
    probe = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                            "format=duration,size:stream=codec_name,width,height,r_frame_rate,"
                            "nb_read_frames,sample_rate,channels,duration", "-of", "json",
                            str(args.video)]).stdout)
    video, audio = probe["streams"]
    assert video["codec_name"] == "h264" and video["width"] == 1080
    assert video["height"] == 1920 and video["r_frame_rate"] == "6/1"
    assert int(video["nb_read_frames"]) == timeline["total_frames"] == 200
    assert abs(float(probe["format"]["duration"]) - 200 / 6) < .02
    assert audio["codec_name"] == "aac" and audio["sample_rate"] == "48000"
    assert audio["channels"] == 2
    run(["ffmpeg", "-v", "error", "-i", str(args.video), "-f", "null", "-"])
    pcm = run(["ffmpeg", "-v", "error", "-i", str(args.video), "-map", "0:a:0",
               "-f", "f32le", "-ar", "48000", "-ac", "2", "-"]).stdout
    samples = np.frombuffer(pcm, dtype="<f4")
    rms = float(np.sqrt(np.mean(samples ** 2)))
    peak = float(np.max(np.abs(samples)))
    assert rms > .001 and .01 < peak < 1
    cap = cv2.VideoCapture(str(args.video))
    midframes = []
    for page in timeline["pages"]:
        frame = page["start_frame"] + page["page_frames"] // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        good, bgr = cap.read()
        assert good, f"Cannot decode page {page['page']} at frame {frame}"
        midframes.append(cv2.resize(bgr, (270, 480)))
    cap.release()
    adjacent_differences = [float(np.mean(np.abs(a.astype(np.int16) - b.astype(np.int16))))
                            for a, b in zip(midframes, midframes[1:])]
    assert min(adjacent_differences) > 1
    report = {"result": "OBJECTIVE_TECHNICAL_PASS", "video": str(args.video),
              "sha256": sha(args.video), "ffprobe": probe,
              "full_video_audio_decode": "PASS", "decoded_audio_rms": rms,
              "decoded_audio_peak": peak, "adjacent_page_midframe_mae": adjacent_differences,
              "caveat": "Media checks do not certify picture aesthetics, narration acting, music quality, lyric pronunciation or distribution rights."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"result": report["result"], "sha256": report["sha256"],
                      "audio_rms": rms, "audio_peak": peak}, indent=2))


if __name__ == "__main__":
    main()
