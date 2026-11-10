# R4 acceptance — review stage

| Gate | State | Evidence / remaining review |
| --- | --- | --- |
| TECHNICAL_PASS | **BLOCKED** | Eight-page MP4 not rendered pending auditions. Page-06 pilot decodes at 1080×1920, 6 fps, 25 frames / 4.167 s. |
| VISUAL_PASS | **BLOCKED** | Eight new matching watercolor pages and captioned contact sheet exist. User visual approval and full-transition review pending. |
| ENGLISH_VOICE_PASS | **BLOCKED** | Two real unprocessed `af_sol` auditions exist; no user hearing verdict on these new lines. |
| AUDIO_PASS | **BLOCKED** | Narration/music/effects stems can be aligned and measured, but full mix and music quality need human listening. |
| EDITORIAL_PASS | **BLOCKED** | Fixed eight-line bilingual script and Xiaohongshu copy prepared; final layout and copy review pending. |
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

Signal, decoding, and source-code inspection do **not** certify voice
performance, music mood, visual appeal, subtitle readability on each phone,
or rights for platform publication. No gate above may be inferred from the
pilot's technical result.
