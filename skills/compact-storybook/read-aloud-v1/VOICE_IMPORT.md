# XHS-EXTERNAL-VOICE-V1 | external narration intake

Use this route when a voice was recorded or synthesized outside Codex. It
verifies source files and records measured audio, but **never awards**
`VOICE_REVIEW`, `READ_ALOUD_PASS`, `COPYRIGHT_PASS` or `PUBLISH_READY`.
An audition license permits private listening only. Formal Xiaohongshu
production also requires an explicit platform/publication grant, reviewed by
a human rights owner. A provider name or model license alone is insufficient.

## Package and manifest

Place `manifest.json`, PCM WAVs and rights evidence in one directory. All paths
inside the manifest are relative to that directory and must remain inside it.
The manifest must include:

```json
{
  "schema_version": "XHS-EXTERNAL-VOICE-V1",
  "story_sha256": "64 lowercase hex characters for frozen story.json",
  "source": {
    "provider": "actual recording or synthesis provider",
    "voice": "voice or performer identifier",
    "source_uri": "traceable account, model or session reference",
    "license_name": "exact agreement or license"
  },
  "rights": {
    "audition": {
      "allowed": true,
      "scope": "private review of this story",
      "evidence_path": "rights/audition.txt",
      "evidence_sha256": "64 lowercase hex characters"
    },
    "publication": {
      "allowed": false,
      "scope": "not yet cleared for Xiaohongshu"
    }
  },
  "pages": [
    {
      "page": 3,
      "wav_path": "audio/page_03.wav",
      "sha256": "64 lowercase hex characters",
      "sample_rate_hz": 24000,
      "duration_s": 6.2,
      "transcript": "A big cloud was hiding the moon. The rabbit’s ears drooped. It felt a little lonely.",
      "processing": "none",
      "content_audit": {"status": "PENDING"}
    }
  ]
}
```

To claim formal publication permission, set `rights.publication.allowed` to
`true` and supply its own `scope`, `evidence_path` and `evidence_sha256`. The
evidence must explicitly cover the intended platform and use. The importer
verifies the file and digest, **not the legal adequacy of the grant**.

For each page, `transcript` must equal the frozen `story.json` English text
byte for byte after JSON decoding. This checks the declared script, **not the
words audible in the WAV**. A person must listen to the entire raw clip and
record whether every sentence is present, the ending is complete and the pace
has not been unnaturally compressed. Only then may `content_audit.status` be
`PASS`, with a named `reviewer`, `heard_exact_text: true`,
`no_truncation: true`, `natural_uncompressed_pace: true`, and a hashed
`evidence_path`/`evidence_sha256` containing the actual listening notes.
`processing` must be `none`; edited timing requires a new unprocessed source
WAV and manifest. An attestation alone does not sign `VOICE_REVIEW`; the user
must hear and accept the performance separately.

The cover (page 00) may be silent and is omitted. Any subset of story pages
may be imported for audition, in ascending page order. A full timeline still
needs **all** story pages, individually approved, plus a human-approved cover
window. No importer output can define page seconds by itself.

## Verify and import

```bash
python3 skills/compact-storybook/read-aloud-v1/import_external_voice.py \
  /path/to/voice-package/manifest.json \
  --story research/xhs-read-aloud-v1/waiting-for-the-moon/story.json \
  --output-dir /path/to/new-empty/verified-voice
```

The program checks the story hash, source and rights declarations, file hashes,
PCM decode, nonblank signal, sampling rate and measured duration. It copies the
verified WAVs and evidence into an empty output directory, then writes
`source_manifest.json` and `import_report.json`. A mismatch blocks import.
The report keeps voice, timeline, rights review and publication **BLOCKED**.

After user voice approval and independent rights review, enter each approved
WAV's relative path, SHA-256 and measured seconds into the existing
`acceptance.json` timeline. Use the existing
[`validate_read_aloud.py`](validate_read_aloud.py) to check one-to-one pages,
per-page approval and narration-derived timing. Later video assembly may reuse
the already proven R2/R3E rendering and audio-mixing tools; this import route
does not change the frozen GIF algorithms.
