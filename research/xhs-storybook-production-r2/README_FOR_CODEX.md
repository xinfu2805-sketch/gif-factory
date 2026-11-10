# XHS-STORYBOOK-R2 | HQ Codex transfer pack

This is the actually approved 33.3-second 8-page crow watercolor source **compressed for transfer**. The 40MB recovery master was not discarded. This zip contains no pre-rendered MP4. **Codex must render using the actual eight illustrations.**

## Quick start

Unzip into an empty folder. Install ffmpeg/ffprobe and Python 3 packages `numpy Pillow opencv-python-headless scipy` (e.g. `pip install numpy pillow opencv-python-headless scipy`).

```bash
python3 source/rebuild_from_artwork.py
```

The resulting file is `reproduced/bedtime_rebuilt_1080p_no_voice.mp4` (33.3s, 1080x1920, H.264 with AAC bedtime music + forest/stone/water FX, but no narrator). The script generates animated pages from the supplied 8 WebP illustrations, not an existing video.

## Compression disclosure

- The authoritative original PNG cards were encoded into WebP quality 95 for transfer; this is a **visually near-identical but not byte-identical** reproduction. Original PNG SHAs and old MP4 SHA cannot be used as expected hashes for this slim transfer.
- The source mixed 33.3-second bed audio was encoded as FLAC. Independent lullaby and Foley stems are additionally supplied as high-quality 96k Opus.
- SHA256 manifest here is for the exact compact source files. Build the movie fresh, then inspect output frames, audio, text, single-jar continuity and record a **new** SHA256; do not claim an expected MP4 identity to the old master.
- Dynamic pages have localized effects but do not have accepted continuous joint movement for the crow.
- Natural Mandarin voice remains **BLOCKED**, robot eSpeak should not be substituted. `voice/merge_voiceover.py` can merge authorized natural speech tracks after a fresh render.
- TimGM6mb musical sample origin license is included for review; social platform distribution clearance remains open. `PUBLISH_READY=BLOCKED` pending natural female voice, artistic and copyright reviews.
- **Do not modify repository main**. Reproduce in a clean environment, commit to research branch only after verified.

## Self-check

Use `sha256sum -c MANIFEST_SHA256.txt` from extracted pack root, then `python3 source/rebuild_from_artwork.py`.
