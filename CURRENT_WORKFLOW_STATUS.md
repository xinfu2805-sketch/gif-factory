# GIF Factory｜current read-aloud workflow status

**Version:** XHS-READ-ALOUD-V1 REVIEW FIX, 2026-11-11 UTC. **Authority:**
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
- `python3 -m unittest discover -s tests -v`: **19/19 passed**, including
  eleven read-aloud contract tests. They cover ordered stages, measured WAV
  timing, human-only gates, source-backed evidence, a reviewed silent cover,
  rejection of a body page without narration, document links and the pilot.
- Wrote a new [Waiting for the Moon story and read-aloud draft](research/xhs-read-aloud-v1/waiting-for-the-moon/STORY_AND_READING.md)
  with expectation → absence → sadness → star companionship → moon → sleep.
  Review-fix pages 02, 03 and 06 match the requested English wording and
  revised Chinese subtitles. The body is **99 English words**, computed from
  `story.json`; its metadata and this document are checked against the text.
  The silent cover is a reviewed timeline exception, while every narrated
  story page still needs a real WAV, file hash, measured duration and
  page-specific human voice approval.
  This draft supersedes the old rabbit project's fixed 33.333-second
  scheduling for future read-aloud production; it does not change or erase
  that research video.
- R2 proves source-based media reconstruction; R3E proves bilingual captions
  and independent voice/music/effects. Their technical successes do not
  certify a general automated publish-ready pipeline.

## Open blockers and next executable task

The new rabbit story text has **not** received actual human editorial or
child-comprehension review: `STORY_REVIEW=BLOCKED`. New narration has not been
generated, measured, auditioned or heard. No new page durations, art,
animation or complete video have been
created for this V1 pilot. The eight human read-aloud criteria, all release
gates and `PUBLISH_READY` are **BLOCKED** in the pilot's
[machine-readable review](research/xhs-read-aloud-v1/waiting-for-the-moon/acceptance.json).
The earlier R2 TimGM6mb lullaby still lacks verified Xiaohongshu distribution
clearance; do not carry its existence into `COPYRIGHT_PASS`.

**Next task:** have Story Expert and Read-Aloud Director review the 99-word
draft against target-age comprehension. Then first try R3E's verified Kokoro
`af_sol` route for two raw English WAV auditions: page 03's lonely moment and
page 07's comforting ending. Keep natural speed, model/voice/version/license
provenance, SHA-256 and complete measured durations; submit both to the user
for listening approval. Only after approval should the Storyboard Director
derive page and turn seconds. Do not reuse the R4 33.333-second timeline or
batch-render a film now.

The new work is in Draft PR #5 against `main`. Keep PR #3, #4 and #5 draft;
do not merge any of them automatically. Use the remote branch ref for the
current SHA, because editing this handoff itself creates a new commit.
