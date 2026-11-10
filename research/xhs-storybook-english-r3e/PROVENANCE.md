# R3E-B source and rights record

| Component | Source | Verified SHA-256 / rights status |
| --- | --- | --- |
| Eight WebP watercolor pages | User-provided R2 source pack, retained on R2 branch | See R2 `MANIFEST_SHA256.txt`; no new image generation |
| 33.3 s picture input | R2 independently reconstructed no-voice MP4 | `7e126011d097b39c69e0f272b0332d4ed83d776c0d598bb0c28b8b32147e60e8` |
| Lullaby input | R2 independent stem | `64799566ad82eabd8340a4be7cde3f655e0c6a7ab77ea54e8865facb89b0e495` |
| Foley input | R2 independent stem | `09b125a614d70396f51fdd32eb8feb25756f022a973797e6c03a9a14c1d4413c` |
| English voice model | [sherpa-onnx official Kokoro v1.1 release](https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_1.tar.bz2) | Archive `b78e1ac42b852e839cceaafbe88f66806bf5860992d1d7b9a3f2ad1198427aed`; model `99db0bc8fd0c5033d249fe922db16768b71b4a6b26cfd93d206fbf66c76efb5f`; voices `e64a5a581d8c2a350d848f51c3121657cd83aa07ed6109172177345874a7244c` |
| Kokoro license | Archive `LICENSE` | Apache-2.0 text `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`; copy in delivery package |
| TimGM6mb sample bank for R2 music | R2 `audio/TimGM6mb_soundfont_license.txt` | GPL-2 attribution text preserved. Its suitability for this exact social-platform distribution remains **unverified**. |

The eight `af_sol` clips are generated locally with `sherpa-onnx==2.0.1`, CPU,
two threads, U.S. English lexicon, speaker ID 1, speed 1.0. The earlier A/B
samples are available in the delivery package; the user selected the `af_sol`
timbre. Full eight-line pronunciation and final mix still need listening.

This record is not a commercial-use clearance certificate. The source-pack
artwork ownership, sampled instrument distribution obligations, and platform
terms must be verified before publication.
