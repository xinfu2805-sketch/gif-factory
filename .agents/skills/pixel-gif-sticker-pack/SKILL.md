---
name: pixel-gif-sticker-pack
description: Create and audit GIF Factory stickers and animations using the complete, versioned GIF Factory sources in this repository; preserve original artwork and distinguish technical validation from visual acceptance.
---

# GIF Factory — repository-level Codex entrypoint

This file is a **discovery entrypoint** for Codex. The authoritative GIF Factory instructions are at the repository root in `SKILL.md`. Do not substitute this abbreviated entrypoint for the root document.

## First steps in each Codex task

1. Identify the **repository root** (for example, `git rev-parse --show-toplevel`). Do not depend on a previous cloud task's home directory, symlink, or `/workspace` path.
2. Read `<repo-root>/SKILL.md` completely. Follow its workflow, user-accepted reference rules, and required visual review; its relative links resolve **from the repository root**.
3. Read `<repo-root>/GUIDE.md` and only the relevant files from `<repo-root>/references/` and `<repo-root>/styles/` for the requested appearance, motion, and output purpose.
4. Reuse repository scripts under `<repo-root>/scripts/` as directed by the authoritative instructions. Use paths rooted in the current checkout. Do not duplicate, fork, or silently modify animation algorithms.
5. Check that Python, Pillow and (when producing MP4 previews) FFmpeg with libx264 are actually available **in this task's runtime**. Do not assume installed dependencies from another Cloud task persist.

## Processing and review

- Distinguish light-motion composition (`scripts/export_pack.py`), HD articulated actions (`scripts/export_keyframes.py`), pixel actions (`scripts/export_pixel_actions.py`), and two-state flips (`scripts/export_lenticular.py`). Do not present a whole-image warp or two-state swap as true skeletal action.
- Preserve the user's accepted likeness, anatomy, appearance and source rights. Generate new pose art only when the requested motion requires it and an image generator is available and authorized.
- Decode the final GIF and audit dimensions, transparency, duration, loop and frame changes. Use `scripts/review_gif.py` when appropriate. Keep technical pass, actual visual review, and user acceptance as distinct statuses.
- Deliver only the output types requested; identify any unverified dependencies, frames, or compatibility claims. Never claim visual/user approval merely from passing scripted checks.

## Repository authority and scope

This entrypoint intentionally references the existing root-level code and documentation. The initial audited root contents were from `a4e2d6d853c91e9ec25d77c7819b3f09e0a11385`; the branch HEAD will change when this entrypoint is added. Verify changes relative to the audited baseline instead of requiring the new HEAD to equal the old SHA.

Never modify unrelated repositories or the frozen GIF Factory algorithms as part of installing/using this skill. Cloud environment publishing and repository-level skill discovery are separate gates; do not claim either is complete without independent verification.
