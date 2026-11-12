# GIF Factory｜current read-aloud workflow status

**Version:** XHS-READ-ALOUD-V1, timeline-integrity and voice-audition update,
2026-11-11 UTC. **Authority:**
`xinfu2805-sketch/gif-factory`. Resolve the latest branch HEAD from GitHub
when a new task starts; historical SHA values below are this recovery's
observations, not permanent aliases for `main`.

## Live authority recovery for this change

| Ref | Observed remote SHA / state |
| --- | --- |
| `main` | `a4e2d6d853c91e9ec25d77c7819b3f09e0a11385` |
| R2 `research/xhs-storybook-production-r2` / [Draft PR #3](https://github.com/xinfu2805-sketch/gif-factory/pull/3) | `9f8d215e145cda5b91d73950b3b8c02c90f959ad`; open, draft, unmerged; base `research/xhs-storybook-publish-v1` |
| R3E `research/xhs-storybook-english-r3e` / [Draft PR #4](https://github.com/xinfu2805-sketch/gif-factory/pull/4) | `8d3a6d4f37c7bb33a6792a5ef8c650bb1c2700a5`; open, draft, unmerged; base R2 branch |
| New `research/xhs-read-aloud-v1` / [Draft PR #5](https://github.com/xinfu2805-sketch/gif-factory/pull/5) | Review-fix starting HEAD `cac7b3f5f0d79a38290c27f9798330088629d1e2`; open, draft, unmerged. Resolve its latest SHA from the remote branch ref. |

Evidence source: `git ls-remote origin refs/heads/main refs/heads/research/xhs-storybook-production-r2 refs/heads/research/xhs-storybook-english-r3e refs/pull/3/head refs/pull/4/head`, public PR HTML, and the connected GitHub tool's `get_pr_info` for PR #3/#4. Direct `gh` GraphQL and REST calls returned **403 Forbidden** in this environment; the connected GitHub tool supplied the verified state, base and merged fields. Both PRs remain separate and unmerged in this work.

## Completed here

- Added the child route in the root and compact-storybook Skills, plus
  [project navigation](AGENTS.md) so new Codex tasks discover
  [XHS-READ-ALOUD-V1](skills/compact-storybook/read-aloud-v1/WORKFLOW.md).
- Versioned stages, roles, evidence requirements, fail/block conditions,
  machine-readable [contract](skills/compact-storybook/read-aloud-v1/workflow_contract.json),
  [acceptance template](skills/compact-storybook/read-aloud-v1/acceptance_template.json)
  and [validator](skills/compact-storybook/read-aloud-v1/validate_read_aloud.py).
- `python3 -m unittest discover -s tests -v`: **23/23 passed**, including
  fifteen read-aloud contract tests. They cover ordered stages, measured WAV
  timing, human-only gates, source-backed evidence, a reviewed silent cover,
  rejection of a body page without narration, and missing, duplicate,
  reordered or role-mismatched pages against the hashed `story.json`.
- Wrote a new [Waiting for the Moon story and read-aloud draft](research/xhs-read-aloud-v1/waiting-for-the-moon/STORY_AND_READING.md)
  with expectation → absence → sadness → star companionship → moon → sleep.
  Review-fix pages 02, 03 and 06 match the requested English wording and
  revised Chinese subtitles. The body is **99 English words**, computed from
  `story.json`; its metadata and this document are checked against the text.
  The silent cover is a reviewed timeline exception, while every narrated
  story page still needs a real WAV, file hash, measured duration and
  page-specific human voice approval.
- Two new raw Kokoro `af_sol` auditions exist: [page 03 loneliness](research/xhs-read-aloud-v1/waiting-for-the-moon/voice/page_03_af_sol_audition.wav)
  (4.983042 s) and [page 07 comforting ending](research/xhs-read-aloud-v1/waiting-for-the-moon/voice/page_07_af_sol_audition.wav)
  (4.922875 s), both 24 kHz mono PCM. The cached official v1.1 model, Apache-2.0
  text, task-local lexicon patch, exact SHA-256 values and objective checks
  are documented in [audition review](research/xhs-read-aloud-v1/waiting-for-the-moon/voice/AUDITION_REVIEW.md).
  The first quote-tokenization warning was corrected; final synthesis logged
  no skipped-word warnings. The [lightweight ZIP](research/xhs-read-aloud-v1/waiting-for-the-moon/delivery/Waiting_for_the_Moon_read_aloud_auditions.zip)
  contains only these two clips and review/source evidence, not model weights.
  This draft supersedes the old rabbit project's fixed 33.333-second
  scheduling for future read-aloud production; it does not change or erase
  that research video.
- R2 proves source-based media reconstruction; R3E proves bilingual captions
  and independent voice/music/effects. Their technical successes do not
  certify a general automated publish-ready pipeline.

## Open blockers and next executable task

The new rabbit story text has **not** received formal human editorial or
child-comprehension signoff: `STORY_REVIEW=BLOCKED`. The two Kokoro audition
WAVs were technically measured, then **heard and rejected by the user for
artistic quality**: `VOICE_REVIEW=BLOCKED`. The five other story pages have no
recorded narration.
No approved full-story page durations, art, animation or complete video have
been created for this V1 pilot. The eight human read-aloud criteria, all release
gates and `PUBLISH_READY` are **BLOCKED** in the pilot's
[machine-readable review](research/xhs-read-aloud-v1/waiting-for-the-moon/acceptance.json).
The earlier R2 TimGM6mb lullaby still lacks verified Xiaohongshu distribution
clearance; do not carry its existence into `COPYRIGHT_PASS`.

**VOICE-PERFORMANCE-R1 update (2026-11-11):** The user heard and rejected the
Kokoro `af_sol` auditions for artistic quality: they sound like English
listening material rather than a warm bedtime narration. Azure Speech F0
preflight stopped at [FIRST_DIVERGENCE](research/xhs-read-aloud-v1/waiting-for-the-moon/voice/VOICE_PERFORMANCE_R1.md): no account credentials, resource region,
F0 proof or quota access; one unauthenticated request was blocked by the
environment proxy with HTTP 403. No Azure audio or ZIP was generated. Official
Microsoft Product Terms grant prebuilt neural voice output use rights to paid
TTS customers only, so F0 is not a proven publication source. `VOICE_REVIEW`,
`READ_ALOUD_PASS` and `PUBLISH_READY` remain BLOCKED.

**Next task:** establish a reachable and authorized voice source and release
rights. Then audition page 03 and 07 in two female voices without changing the
frozen text; submit the real WAVs for user listening. Only after approval should
the Storyboard Director derive timings. Do not reuse the fixed 33.333-second
timeline or batch-render a film now.

**VOICE-SOURCE-INTEGRATION-R1 update (2026-11-11):** Added the
[external WAV intake contract](skills/compact-storybook/read-aloud-v1/VOICE_IMPORT.md)
and [verifier/importer](skills/compact-storybook/read-aloud-v1/import_external_voice.py).
It binds any supplied page clip to the unchanged 99-word `story.json`, checks
real PCM WAV decode, SHA-256, sample rate, measured duration and a nonblank
signal, and separates private audition permission from Xiaohongshu publication
permission. A named human must attest to every spoken sentence, full ending and
natural pace; that is still separate from the user's artistic voice approval.
No external qualified WAV was supplied in this task, so the importer has only
temporary synthetic **test fixtures** and there is no new audition audio or
timeline. `VOICE_REVIEW`, `READ_ALOUD_PASS`, `COPYRIGHT_PASS` and
`PUBLISH_READY` remain BLOCKED. The new entry does not alter the frozen GIF
algorithms, `main`, or the story text. Keep Draft PR #5 open and unmerged.

**Next executable task:** supply a legitimately recorded or synthesized female
English narration package using the manifest contract. Import for audition,
listen to each page with the user, verify publication rights separately, then
derive a complete timeline from the measured, approved audio.

The new work is in Draft PR #5 against `main`. Keep PR #3, #4 and #5 draft;
do not merge any of them automatically. Use the remote branch ref for the
current SHA, because editing this handoff itself creates a new commit.

## GIF-FIRST-ACTION-R1 update (2026-11-12)

- Added [GIF animation gate](skills/compact-storybook/read-aloud-v1/GIF_ACTION_GATE.md) to the scoped read-aloud route. Character acting is checked as one-shot GIF before full MP4 production; this does not alter the story-first / approved-voice timing authority.
- Added [one-shot GIF exporter](scripts/export_storybook_gif.py) and [two action-preflight regression tests](tests/test_storybook_gif_action.py). Local prototype tests passed 2/2; full repository suite remains to be rerun in its environment. Pixel change and GIF existence do **not** grant ACTION_PASS.
- No genuine rabbit pose atlas has been approved in this work. The requested sad / falling-asleep actions still need multiple identity-stable source poses; **ACTION_PASS remains BLOCKED**. VOICE_REVIEW, COPYRIGHT_PASS and PUBLISH_READY are unchanged / BLOCKED.
- Main is untouched; the additions are in the existing research branch and Draft PR #5. No merge was performed.
