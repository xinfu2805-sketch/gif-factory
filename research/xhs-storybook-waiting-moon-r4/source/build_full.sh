#!/usr/bin/env bash
# Offline rebuild from the eight original artwork files and approved voice clips.
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 MUSIC_SOURCE OUTPUT_DIR" >&2
  exit 2
fi
root_dir="$(cd "$(dirname "$0")/.." && pwd)"
music_source="$1"
output_dir="$2"
mkdir -p "$output_dir/audio"
python3 "$root_dir/source/build_timeline.py" > "$output_dir/timeline_build.log"
python3 "$root_dir/source/make_foley.py" --output "$output_dir/foley_original.wav"
python3 "$root_dir/source/mix_audio.py" --music "$music_source" \
  --foley "$output_dir/foley_original.wav" --output-dir "$output_dir/audio" \
  > "$output_dir/mix_build.log"
python3 "$root_dir/source/render_story.py" \
  --output "$output_dir/waiting_for_the_moon_picture.mp4"
ffmpeg -hide_banner -v error -y \
  -i "$output_dir/waiting_for_the_moon_picture.mp4" \
  -i "$output_dir/audio/mix.wav" -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart -t 33.333333 \
  "$output_dir/Waiting_for_the_Moon_R4.mp4"
python3 "$root_dir/source/verify_delivery.py" \
  --video "$output_dir/Waiting_for_the_Moon_R4.mp4" \
  --output "$output_dir/technical_report.json"
