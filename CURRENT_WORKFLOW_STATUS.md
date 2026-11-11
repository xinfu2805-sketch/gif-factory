# GIF Factory｜current read-aloud workflow status

**Version:** XHS-READ-ALOUD-V1, 2026-11-11 UTC. **Authority:**
`xinfu2805-sketch/gif-factory`. Resolve the latest branch HEAD from GitHub
when a new task starts; historical SHA values below are this recovery's
observations, not permanent aliases for `main`.

## Live authority recovery for this change

| Ref | Observed remote SHA / state |
| --- | --- |
| `main` | `a4e2d6d853c91e9ec25d77c7819b3f09e0a11385` |
| R2 `research/xhs-storybook-production-r2` / [Draft PR #3](https://github.com/xinfu2805-sketch/gif-factory/pull/3) | `9f8d215e145cda5b91d73950b3b8c02c90f959ad`; open, draft, unmerged; base `research/xhs-storybook-publish-v1` |
| R3E `research/xhs-storybook-english-r3e` / [Draft PR #4](https://github.com/xinfu2805-sketch/gif-factory/pull/4) | `8d3a6d4f37c7bb33a6792a5ef8c650bb1c2700a5`; open, draft, unmerged; base R2 branch |
| New `research/xhs-read-aloud-v1` / [Draft PR #5](https://github.com/xinfu2805-sketch/gif-factory/pull/5) | Branched from the observed `main`; open, draft, unmerged. Resolve its latest SHA from the remote branch ref. |

Evidence source: `git ls-remote origin refs/heads/main refs/heads/research/xhs-storybook-production-r2 refs/heads/research/xhs-storybook-english-r3e refs/pull/3/head refs/pull/4/head`, public PR HTML, and the connected GitHub tool's `get_pr_info` for PR #3/#4. Direct `gh` GraphQL and REST calls returned **403 Forbidden** in this environment; the connected GitHub tool supplied the verified state, base and merged fields. Both PRs remain separate and unmerged in this work.

## Completed here

- Added the child route in the root and compact-storybook Skills, plus
  [project navigation](AGENTS.md) so new Codex tasks discover
  [XHS-READ-ALOUD-V1](skills/compact-storybook/read-aloud-v1/WORKFLOW.md).
- Versioned stages, roles, evidence requirements, fail/block conditions,
  machine-readable [contract](skills/compact-storybook/read-aloud-v1/workflow_contract.json),
  [acceptance template](skills/compact-storybook/read-aloud-v1/acceptance_template.json)
  and [validator](skills/compact-storybook/read-aloud-v1/validate_read_aloud.py).
- `python3 -m unittest discover -s tests -v`: 17/17 passed, including nine
  new contract tests for ordered stages, measured narration timing, human-only
  gates, source-backed evidence, document links and the pilot draft.
- Wrote a new [Waiting for the Moon story and read-aloud draft](research/xhs-read-aloud-v1/waiting-for-the-moon/STORY_AND_READING.md)
  with expectation → absence → sadness → star companionship → moon → sleep.
  This draft supersedes the old rabbit project's fixed 33.333-second
  scheduling for future read-aloud production; it does not change or erase
  that research video.
- R2 proves source-based media reconstruction; R3E proves bilingual captions
  and independent voice/music/effects. Their technical successes do not
  certify a general automated publish-ready pipeline.

## Open blockers and next executable task

The new rabbit narration has not been generated, measured, auditioned or
heard. No new page durations, art, animation or complete video have been
created for this V1 pilot. The eight human read-aloud criteria, all release
gates and `PUBLISH_READY` are **BLOCKED** in the pilot's
[machine-readable review](research/xhs-read-aloud-v1/waiting-for-the-moon/acceptance.json).
The earlier R2 TimGM6mb lullaby still lacks verified Xiaohongshu distribution
clearance; do not carry its existence into `COPYRIGHT_PASS`.

**Next task:** have Story Expert and Read-Aloud Director review the 91-word
draft against target-age comprehension, then make two raw voice auditions
(sadness and comfort passages) with a traceable permitted English voice.
Record human listening notes and exact WAV durations. Only after approval
should the Storyboard Director derive page and turn seconds. Do not reuse the
R4 33.333-second timeline or batch-render a film now.

The new work is in Draft PR #5 against `main`. Keep PR #3, #4 and #5 draft;
do not merge any of them automatically. Use the remote branch ref for the
current SHA, because editing this handoff itself creates a new commit.
