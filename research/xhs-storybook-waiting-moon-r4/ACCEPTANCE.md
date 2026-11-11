# R4 acceptance — complete technical render, publication pending

| Gate | State | Evidence / remaining review |
| --- | --- | --- |
| TECHNICAL_PASS | **PASS** | Fresh 8-page H.264/AAC MP4 fully decodes: 1080×1920, 200 frames at 6 fps, 33.333 s; 48 kHz stereo AAC has nonzero RMS/peak. A clean source-only rebuild reproduced the exact MP4 SHA-256. `review/final_technical_report.json` and `review/clean_rebuild_evidence.txt`. |
| VISUAL_PASS | **BLOCKED** | Eight new matching watercolor pages and all page/turn contact sheets inspected, but full-motion artistic approval is pending. |
| ENGLISH_VOICE_PASS | **BLOCKED** | User said the two new `af_sol` auditions were “不错”; the selected voice is used. All eight final lines still need a full listen for pronunciation and acting. |
| AUDIO_PASS | **BLOCKED** | Narration/music/effects stems align; decoded MP4 audio is non-silent. Human listening to the final mix and music quality is pending. |
| EDITORIAL_PASS | **BLOCKED** | Fixed eight-line bilingual script and Xiaohongshu copy prepared; mobile layout and final copy approval pending. |
| COPYRIGHT_PASS | **BLOCKED** | Kokoro license preserved; TimGM6mb sample-bank rights for platform distribution are unresolved. |
| PUBLISH_READY | **BLOCKED** | Full video, subjective reviews and rights clearance remain open. |

## Evidence already collected

- `timeline.json`: 200 frames / 33.333 s at true 6 fps; seven 3-frame turns;
  page-specific voice windows. Every narration clip fits its page without
  time stretching or clipping.
- `review/eight_artwork_contact.jpg`: eight new static watercolor pages from
  the same rabbit reference, left ear folded, right ear upright, green scarf.
- `review/captioned_contact.jpg`: independently rendered English-first,
  Chinese-second typography in the lower paper area; `review/cover.png`.
- `review/page_06_pilot.mp4` and contact: separately moving generated cloud
  sprite, moon reveal, individual star and grass accents. The rabbit and camera
  remain fixed. This is intentionally light animation, not joint action.
- `voice/audition_beginning.wav` and `voice/audition_ending.wav`: 8.849 s and
  9.891 s, respectively, real 24 kHz mono PCM with no backing track. The
  earlier skipped-word error was corrected with task-local lexicon entry for
  “waited”; final synthesis emitted no missing-word warnings.
- `voice/generation.json`: source lines, generated file SHA-256, duration,
  signal peaks, engine parameters and local lexicon hash.
- `review/final_pages_contact.jpg` and `review/turns_contact.jpg`: decoded
  frames from the new MP4, not the pre-render source images.
- `review/final_technical_report.json`: complete decode, frame rate/size,
  AAC signal test and SHA-256 of the final MP4. Final file SHA-256 is
  `373581ad598c588e200ef511d44cf77116ce0c10adae07fd09a6858c3ff68bea`.
- `review/clean_rebuild_evidence.txt`: fresh extraction of source inputs only,
  with MP4 excluded, then `source/build_full.sh`; rebuilt SHA-256 is identical.

Signal, decoding, and source-code inspection do **not** certify voice
performance, music mood, visual appeal, subtitle readability on each phone,
or rights for platform publication. No gate above may be inferred from the
pilot's technical result.
