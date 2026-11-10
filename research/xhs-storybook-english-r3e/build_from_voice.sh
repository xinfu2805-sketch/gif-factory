#!/usr/bin/env bash
set -euo pipefail

# Small offline work pack: input has base_video.mp4, artwork/, audio/, voice/.
# This regenerates the bilingual picture and final mix from the supplied
# independently checkable eight Kokoro WAVs; no pre-rendered final MP4 is input.
input_dir="$(realpath "$1")"
output_dir="$(realpath -m "$2")"
script_dir="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$output_dir/voice" "$output_dir/picture" "$output_dir/audio"
cp "$input_dir/voice/"*.wav "$input_dir/voice/timeline.json" "$output_dir/voice/"
python "$script_dir/render_bilingual.py" --base-video "$input_dir/base_video.mp4" \
  --artwork-dir "$input_dir/artwork" --out-dir "$output_dir/picture"
python "$script_dir/mix_audio.py" --voice-dir "$output_dir/voice" \
  --music "$input_dir/audio/lullaby_original_33s.opus" \
  --foley "$input_dir/audio/foley_original_33s.opus" --out-dir "$output_dir/audio"
ffmpeg -hide_banner -loglevel error -y \
  -i "$output_dir/picture/bilingual_picture.mp4" -i "$output_dir/audio/final_mix.wav" \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -t 33.3 \
  -movflags +faststart "$output_dir/The_Thirsty_Crow_bilingual_1080x1920.mp4"
python "$script_dir/verify_delivery.py" --output "$output_dir" --report "$output_dir/technical_report.json"
find "$output_dir" -maxdepth 3 -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$output_dir/SHA256SUMS"
