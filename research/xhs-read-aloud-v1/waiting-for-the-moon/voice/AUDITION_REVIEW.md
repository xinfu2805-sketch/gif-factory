# Waiting for the Moon｜raw English voice auditions

Two real, unprocessed WAVs were generated for **listening review only**:

| Page / intention | Raw WAV | Measured length | Source text |
| --- | --- | --- | --- |
| 03 · mild loneliness | [page_03_af_sol_audition.wav](page_03_af_sol_audition.wav) | 4.983042 s | “A big cloud was hiding the moon. The rabbit’s ears drooped. It felt a little lonely.” |
| 07 · safe bedtime close | [page_07_af_sol_audition.wav](page_07_af_sol_audition.wav) | 4.922875 s | “Good night, Moon,” whispered the rabbit. It curled up, feeling safe, and fell asleep. |

The official sherpa-onnx [Kokoro multi-lang v1.1 release](https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_1.tar.bz2)
was already cached locally. The same R3E `af_sol` speaker ID 1 was used with
`sherpa-onnx==2.0.1`, CPU, 2 threads, speed 1.0, U.S. English lexicon. The
official `model.onnx` SHA-256 is
`99db0bc8fd0c5033d249fe922db16768b71b4a6b26cfd93d206fbf66c76efb5f`;
`voices.bin` is
`e64a5a581d8c2a350d848f51c3121657cd83aa07ed6109172177345874a7244c`.
The model archive's [Apache-2.0 license text](KOKORO_LICENSE_APACHE_2.txt)
has SHA-256
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
No network download, paid API, music, reverb, pitch shift, speed change or
postprocessing was used.

The official lexicon lacked `rabbit's`, so [one local pronunciation entry](lexicon_patch.txt)
was added to a task-local lexicon; the cached official model was unchanged.
The first exploratory pass treated quotation marks as part of `Good` and
logged a skipped word. That pass was discarded. The final generator removes
quote *glyphs only in the TTS input*, preserving the exact source script in
`story.json`; its tokenizer warning log is empty. The source and every
parameter/hash are in [generation_report.json](generation_report.json).

[verification.json](verification.json) records the actual WAV headers,
FFmpeg full decode, peak/RMS levels, leading/trailing silence and hashes.
These are **technical** checks. A human has not yet determined whether
“rabbit’s,” the small sadness, “Good night,” or the final settling sound
natural. `VOICE_REVIEW`, `READ_ALOUD_PASS` and `PUBLISH_READY` remain
**BLOCKED**. Both clips must be heard and explicitly accepted before any
formal narration-derived timeline is signed.

To regenerate locally from the official model package:

```sh
python3 generate_auditions.py --model-dir /path/to/kokoro-multi-lang-v1_1 --output-dir voice
```
