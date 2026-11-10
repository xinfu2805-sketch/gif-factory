# Waiting for the Moon | R4 production study

New eight-page rabbit watercolor story. This directory is isolated from the
R2/R3E renderers and GIF Factory's frozen algorithms. The fixed English and
Chinese copy is in `timeline.json`; page artwork and its reference sheet are
in `artwork/`. The source files generate the voice, timeline, local light
motion, original sound effects, and separate audio mix. The renderer never
uses an older story video as input.

## Current review point

The eight new watercolor pages, bilingual caption stills, cover, and a
4.17-second page-06 motion pilot are complete. Two unprocessed English
`af_sol` auditions are in `voice/`. A human has **not** yet approved the new
sentences or the picture pages. Therefore the 8-page video is deliberately
not rendered. See `ACCEPTANCE.md` before interpreting any test result.

## Rebuild inputs and commands

Requires Python 3 with Pillow, NumPy and `sherpa-onnx==2.0.1`, FFmpeg, Noto
Serif and Noto Serif CJK fonts. For offline voice regeneration also provide
the official `kokoro-multi-lang-v1_1` sherpa-onnx package (`model.onnx`,
`voices.bin`, `tokens.txt`, `lexicon-us-en.txt`). This 300+ MB model is not in
the lightweight work package. The generated 24 kHz PCM voice clips are
included. `generate_voice.py` writes its one extra pronunciation to a local
lexicon without changing the official cached model.

From this directory, after sourcing the R2 lullaby stem and reviewing its
rights status:

```sh
python3 source/build_timeline.py
python3 source/make_foley.py --output /tmp/moon-foley.wav
python3 source/mix_audio.py --music /path/to/lullaby_original_33s.opus \
  --foley /tmp/moon-foley.wav --output-dir /tmp/moon-audio
python3 source/render_story.py --pilot-page 6 --output /tmp/moon-pilot.mp4
```

The full renderer is held for the voice and visual review. Once those are
accepted, `python3 source/render_story.py --output /tmp/moon-picture.mp4`
will produce a new 200-frame, true-6fps picture track. Mux with the freshly
created mix as AAC without changing the frame rate. Recheck every output.

The R2 lullaby is retained as a **provisional research stem** because the
original soundfont's Xiaohongshu distribution clearance remains unresolved.
The seven page-turn effects, slow wind, and sparse star ticks are generated
locally by `make_foley.py`, with no outside recordings.
