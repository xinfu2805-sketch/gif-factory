# Waiting for the Moon | R4 production study

New eight-page rabbit watercolor story. This directory is isolated from the
R2/R3E renderers and GIF Factory's frozen algorithms. The fixed English and
Chinese copy is in `timeline.json`; page artwork and its reference sheet are
in `artwork/`. The source files generate the voice, timeline, local light
motion, original sound effects, and separate audio mix. The renderer never
uses an older story video as input.

## Current deliverable

The eight new watercolor pages, bilingual caption stills, cover, and a
4.17-second page-06 motion pilot are complete. The user described the two
unprocessed English `af_sol` auditions as “不错”; the same voice was then
used for the 33.333-second eight-page video. The full MP4, separate stems,
and SHA-256 manifest are in the downloadable release package. The voice
choice is accepted for this render, while final mix listening, image quality,
and music rights still need review. See `ACCEPTANCE.md`.

## Rebuild inputs and commands

Requires Python 3 with `requirements-build.txt`, FFmpeg, Noto Serif and
Noto Serif CJK fonts. For offline voice regeneration, also install
`sherpa-onnx==2.0.1` and provide
the official `kokoro-multi-lang-v1_1` sherpa-onnx package (`model.onnx`,
`voices.bin`, `tokens.txt`, `lexicon-us-en.txt`). This 300+ MB model is not in
the lightweight work package. The generated 24 kHz PCM voice clips are
included. `generate_voice.py` writes its one extra pronunciation to a local
lexicon without changing the official cached model.

From this directory, after sourcing the R2 lullaby stem and reviewing its
rights status, the full offline-from-voice build is:

```sh
./source/build_full.sh /path/to/lullaby_original_33s.opus /tmp/moon-output
```

This builds a new 200-frame, true-6fps picture track from the eight PNG pages,
generates original soft effects, aligns the independent voice/music/effects
tracks, muxes AAC, and runs objective media verification. It never copies
an older story MP4. The package includes the eight approved-voice source
clips for fully offline rebuild; no model download is needed for that route.

The R2 lullaby is retained as a **provisional research stem** because the
original soundfont's Xiaohongshu distribution clearance remains unresolved.
The seven page-turn effects, slow wind, and sparse star ticks are generated
locally by `make_foley.py`, with no outside recordings.
