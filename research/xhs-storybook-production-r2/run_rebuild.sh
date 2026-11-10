#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$project_dir"
sha256sum -c MANIFEST_SHA256.txt
python3 source/rebuild_from_artwork.py
video=reproduced/bedtime_rebuilt_1080p_no_voice.mp4
ffmpeg -v error -i "$video" -f null -
ffprobe -v error -count_frames \
  -show_entries format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames \
  -of json "$video"
sha256sum "$video"
