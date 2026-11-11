# XHS-READ-ALOUD-V1｜儿童睡前有声绘本

**Version:** XHS-READ-ALOUD-V1 (2026-11-11). Applies to children's bedtime
read-aloud stories, English narrated picture books, bilingual subtitled books,
and parent-child reading shorts. This is a routed extension of the
[compact-storybook Skill](../SKILL.md), not a replacement for its short 3-second
pages. Ordinary GIFs, stickers, posters and non-narrated short storybooks keep
their existing routes.

## Production invariant

**Story → story review → child-friendly read-aloud text → voice audition and
read-aloud direction → measured narration → storyboard timing → art → motion
and page turns → subtitles and separate audio stems → full audiovisual review
→ rights and technical review → release MP4.** The story and natural reading
determine duration. Never trim a final word, speed up speech, extend idle art,
or impose a preselected video duration to make a story fit.

1080×1920 vertical, around eight pages, 50–70 seconds and 70–100 English body
words are **starting suggestions**, not gates. Adjust to the story and
recorded read-aloud. English is the primary spoken and written line; Chinese
is an independently rendered smaller translation. Keep a watercolor paper
look, consistent character and low-stimulation bedtime sound. Each page must
advance an event, emotion or understanding. A static wait cannot fill time.

## Stages and evidence

The IDs and order are machine-readable in [workflow_contract.json](workflow_contract.json).
The owner is a review responsibility, not a claim that an expert has reviewed
anything. A stage is `PASS` only with inspectable evidence and the required
review; `FAIL` means observed quality failure; `BLOCKED` means input, source,
rights or human judgment is missing. Do not convert `BLOCKED` to `PASS` from
file existence alone.

| Stage / owner | Input → output | Pass evidence / FAIL or BLOCKED |
| --- | --- | --- |
| `STORY` · Story Expert | Theme, age range → complete cause, development, turn, resolution and emotion map | Script with concrete beats. FAIL if it is a repeated waiting scene or lacks a turn/ending; BLOCKED if theme or audience is unknown. |
| `STORY_REVIEW` · Story Expert + Quality Director | Story draft → child comprehension and bedtime editorial notes | Actual reviewer observations for plot and language. FAIL if a child cannot follow cause and outcome; BLOCKED until human review. |
| `READING_SCRIPT` · Read-Aloud Director | Reviewed story → speakable English, Chinese translation, pronunciation and pause cues | Page-aligned text and word count, no forced page seconds. FAIL for unnatural prose, literal translation or missing event; BLOCKED if story review is open. |
| `VOICE_REVIEW` · Read-Aloud Director + Sound Director | Reading script, licensed voice option → two raw auditions, chosen performance, full line recordings | Model/source/license and two audition files; human notes on diction, breath, warmth and pauses. FAIL for skipped words, mechanical acting or clipping; BLOCKED without listening or usable rights. |
| `TIMELINE` · Storyboard Director | Approved, measured narration clips → page windows, comprehension holds, turn windows and storyboard | Every **story page** cites its real WAV, SHA-256, measured seconds and page-specific human voice approval; page time covers speech plus meaning/visual hold. A declared **silent cover at page 0** may instead use human-approved display and turn seconds. Total is derived. FAIL if speech is cut or an action precedes its narration; BLOCKED before voice approval. |
| `ART` · Watercolor Artist | Timed storyboard, reference identity → model sheet, page paintings and clean subtitle zones | Contact sheet and source hashes, stable face/palette/props. FAIL for identity drift, wrong text embedded in art or unreadable safe area; BLOCKED pending visual review. |
| `ANIMATION` · Animation Director | Approved art and timed beats → local character/environment/action layers and page turns | Decoded first/middle/last and contact frames, object-state continuity. FAIL for duplicate props, false whole-page motion or unresolved contact; BLOCKED without actual frame review. |
| `SOUND_SUBTITLES` · Sound Director | Timed clips, licensed music/effects, translations → separate voice/music/FX, ducked mix, bilingual captions | Signal report, per-stem listen notes, subtitle proof. FAIL for masking, mismatch, harsh sound or wrong glyphs; BLOCKED for music source, translation or listening gaps. |
| `FULL_AV_REVIEW` · Quality Director with all directors | Full draft → page-by-page sight/listen record and eight read-aloud criteria | Human observations on story, reading, movement, sync and ending at actual viewing size. FAIL for material mismatch; BLOCKED for any unreviewed criterion. |
| `RIGHTS_TECH` · Quality Director | Full draft and asset ledger → ffprobe/decode/hash results and platform-use rights record | Exact media stats, independent stems, traceable asset licenses. FAIL for corrupt/misaligned output or denied rights; BLOCKED for unresolved platform rights. |
| `EXPORT` · Quality Director | All approved gates → MP4, cover, title/copy/tags, source work pack, hashes | Reviewable package and delivery manifest. FAIL for incomplete package; BLOCKED while a release gate is open. |

## Read-aloud gate

`READ_ALOUD_PASS` is separate from technical, visual, action, audio, editorial,
copyright and publication gates. It requires **all eight** human decisions:

1. `STORY_COMPLETE` — clear cause, development, turn and ending.
2. `CHILD_COMPREHENSION` — target-age child can follow motive and outcome.
3. `NARRATION_NATURAL` — accurate pronunciation and expressive, warm speech.
4. `READING_RHYTHM` — speech, silence and turns serve meaning.
5. `AUDIO_VISUAL_SYNC` — illustrated events match the words at that moment.
6. `PAGE_READING_TIME` — each page allows listening and looking without padding.
7. `BEDTIME_SUITABILITY` — sight and sound are calm, gentle and low stimulus.
8. `ENDING_QUALITY` — a natural, settled close without abrupt cutoff.

Machine checks may measure word count, recorded clip duration, page window,
decoded frames, levels and event markers. They cannot decide whether a child
understands the story or whether narration feels natural. Every `PASS` for the
eight criteria needs a named human reviewer, a specific observation and a
hashed evidence file. `READ_ALOUD_PASS` remains `BLOCKED` until the full
human review is complete. Technical `PASS` never implies publication `PASS`.

### Timeline cover exception

The title/cover may be silent **only** as page 0 with `role: "cover"`. It has
`display_duration_s`, `turn_s` and a `cover_review` decision with a named
human, `timing_approval` evidence and a SHA-256. The review repeats the exact
approved display and turn seconds. It must not claim an audio
file or `voice_duration_s`. Body pages use `role: "story"` and retain a real
WAV file, its SHA-256, measured duration, `audio_approved: true` and a
page-specific human `voice_review` with `voice_approval` evidence bound to
that WAV's SHA-256. The total
is the sum of page display times and turns; there is no fixed target duration.
The validator rejects a silent body page or an unreviewed cover. A cover
exception does not waive the `VOICE_REVIEW` gate for the narrated story.

Copy [acceptance_template.json](acceptance_template.json) into a project and
run `python3 skills/compact-storybook/read-aloud-v1/validate_read_aloud.py
PROJECT/acceptance.json --root PROJECT`. The validator checks ordered stages,
source-backed evidence, narration-derived timing and gate dependencies; it
does **not** make subjective decisions for reviewers. Contract tests are in
[`tests/test_read_aloud_contract.py`](../../../tests/test_read_aloud_contract.py).

## Existing proof and limit

R2 demonstrated source-based eight-page video rebuilding; R3E demonstrated
English clips, bilingual lower-page text and separate music/effects mixing.
Neither validates a general automatic story-to-release system. The R4 rabbit
study is a useful art/voice reference, but its 33.333-second schedule was set
before the new story-first read-aloud standard, so it is **not** this V1
pilot's timeline. See [current status](../../../CURRENT_WORKFLOW_STATUS.md)
and the [new rabbit pilot](../../../research/xhs-read-aloud-v1/waiting-for-the-moon/STORY_AND_READING.md).
