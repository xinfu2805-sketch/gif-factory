# The Thirsty Crow | R3E bilingual edition

This branch adds English narration and bilingual lower-page typography to the
accepted R2 eight-page picture. It does not rebuild the crow, redraw artwork,
or change the R2 animation renderer. The final input is the verified 33.3 s R2
no-voice MP4, eight original WebP pages, and independent R2 music/foley stems.

## Rebuild

Python 3.12, FFmpeg, Noto Serif and Noto Serif CJK SC fonts are required. Put
the input files in the layout documented in `build.sh`. Create a fresh virtual
environment, install `requirements.txt`, then run:

```sh
./build.sh /path/to/input /path/to/output
```

The four official Kokoro model files are too large for the lightweight source
bundle. Supply the verified sherpa-onnx Kokoro 82M v1.1 English model separately:
`model.onnx`, `voices.bin`, `tokens.txt`, `lexicon-us-en.txt`. Speaker 1 is
`af_sol`; CPU threads 2; speed 1.0. The eight generated voice WAV files are
included in the delivery pack so the accepted voice can be audited without
downloading the weights. `timeline.json` has every page's English, Chinese,
and voice start/end times.

For a fully offline rebuild from the supplied voice clips, use
`build_from_voice.sh INPUT_DIR OUTPUT_DIR`; `INPUT_DIR/voice` contains the eight
WAVs and `timeline.json`. This still renders all 799 bilingual picture frames
and the final audio mix afresh. It never takes the final MP4 as an input.

The video renderer replaces the printed Chinese copy region with paper sampled
from the same watercolor page, then renders English first and Chinese below.
It uses the R2 picture as input and copies the original frame rate and timing.
The audio mixer retains voice, music, and foley as separate WAV files. Music is
gently lowered during speech and restored between lines.

## Publication gate

This production experiment is not yet signed for publication. Known R2 crow
joint motion shortcomings remain, and the TimGM6mb soundfont provenance does
not by itself establish all rights needed for a Xiaohongshu release. User
approval of the `af_sol` voice sample also does not certify every newly
generated sentence or the final mix. See `ACCEPTANCE.md` for tested items and
explicit blocks.
