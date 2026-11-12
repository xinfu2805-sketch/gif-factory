"""Regressions for external WAV intake; all media here is temporary test data."""
import copy
import hashlib
import json
import math
import subprocess
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "skills/compact-storybook/read-aloud-v1"
sys.path.insert(0, str(SPEC))
from import_external_voice import verify  # noqa: E402


class ExternalVoiceImportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.story = self.base / "story.json"
        self.story.write_text(json.dumps({"pages": [
            {"page": 0, "role": "cover", "english": "Title."},
            {"page": 1, "role": "story", "english": "The rabbit waited. The moon came out."},
            {"page": 2, "role": "story", "english": "Good night, Moon."}]}))
        self.wav = self.base / "page_01.wav"
        samples = b"".join(struct.pack("<h", int(8000 * math.sin(i * 2 * math.pi * 440 / 16000)))
                           for i in range(16000))
        with wave.open(str(self.wav), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(16000)
            out.writeframes(samples)
        proof = self.base / "rights.txt"
        proof.write_text("Audition rights granted; publication rights not established.")
        self.manifest = {
            "schema_version": "XHS-EXTERNAL-VOICE-V1",
            "story_sha256": self.digest(self.story),
            "source": {"provider": "external studio", "voice": "licensed female voice",
                       "source_uri": "provider record", "license_name": "audition agreement"},
            "rights": {
                "audition": {"allowed": True, "scope": "private listening",
                             "evidence_path": "rights.txt", "evidence_sha256": self.digest(proof)},
                "publication": {"allowed": False, "scope": "not yet cleared"}},
            "pages": [{"page": 1, "wav_path": "page_01.wav", "sha256": self.digest(self.wav),
                       "sample_rate_hz": 16000, "duration_s": 1.0,
                       "transcript": "The rabbit waited. The moon came out.",
                       "processing": "none", "content_audit": {"status": "PENDING"}}]}

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def errors(self, manifest=None):
        return verify(manifest or self.manifest, self.base, self.story)[0]

    def test_audition_only_import_is_technical_candidate_not_review_pass(self):
        errors, measured, _ = verify(self.manifest, self.base, self.story)
        self.assertEqual(errors, [])
        self.assertEqual(measured[0]["sample_rate_hz"], 16000)
        self.assertEqual(measured[0]["duration_s"], 1.0)
        self.assertLess(measured[0]["rms_dbfs"], 0)

    def test_cli_copies_verified_source_and_keeps_gates_blocked(self):
        manifest_path = self.base / "manifest.json"
        manifest_path.write_text(json.dumps(self.manifest))
        destination = self.base / "imported"
        result = subprocess.run([sys.executable, str(SPEC / "import_external_voice.py"),
                                 str(manifest_path), "--story", str(self.story),
                                 "--output-dir", str(destination)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.digest(destination / "page_01.wav"), self.digest(self.wav))
        report = json.loads((destination / "import_report.json").read_text())
        self.assertFalse(report["publication_permission_declared"])
        self.assertFalse(report["content_audit_complete"])
        self.assertEqual(report["voice_review"], "BLOCKED_PENDING_USER_LISTENING")
        self.assertEqual(report["timeline"], "BLOCKED_PENDING_VOICE_REVIEW")

    def test_frozen_story_text_and_hash_must_match(self):
        bad = copy.deepcopy(self.manifest)
        bad["story_sha256"] = "0" * 64
        bad["pages"][0]["transcript"] = "The rabbit slept."
        self.assertTrue(any("story mismatch" in e for e in self.errors(bad)))
        self.assertTrue(any("transcript must exactly match" in e for e in self.errors(bad)))

    def test_wav_hash_rate_and_duration_are_measured(self):
        bad = copy.deepcopy(self.manifest)
        bad["pages"][0].update(sha256="0" * 64, sample_rate_hz=24000, duration_s=.5)
        errors = self.errors(bad)
        self.assertTrue(any("SHA-256 mismatch" in e for e in errors))
        self.assertTrue(any("sample rate differs" in e for e in errors))
        self.assertTrue(any("duration differs" in e for e in errors))

    def test_silent_wav_is_rejected(self):
        with wave.open(str(self.wav), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(16000)
            out.writeframes(b"\0\0" * 16000)
        self.manifest["pages"][0]["sha256"] = self.digest(self.wav)
        self.assertTrue(any("near-silent" in e for e in self.errors()))

    def test_speed_change_and_unsubstantiated_content_audit_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad["pages"][0]["processing"] = "time_stretch_1.3x"
        bad["pages"][0]["content_audit"] = {"status": "PASS", "reviewer": "Someone"}
        errors = self.errors(bad)
        self.assertTrue(any("speed or time processing" in e for e in errors))
        self.assertTrue(any("human text, ending and pace attestation" in e for e in errors))

    def test_publication_claim_needs_hashed_evidence(self):
        bad = copy.deepcopy(self.manifest)
        bad["rights"]["publication"] = {"allowed": True, "scope": "Xiaohongshu commercial release"}
        self.assertTrue(any("rights.publication: lowercase SHA-256 required" in e for e in self.errors(bad)))

    def test_cover_and_duplicate_page_cannot_be_imported_as_story(self):
        bad = copy.deepcopy(self.manifest)
        bad["pages"].append(copy.deepcopy(bad["pages"][0]))
        bad["pages"].append({"page": 0})
        errors = self.errors(bad)
        self.assertTrue(any("unique story page number" in e for e in errors))

    def test_paths_must_stay_inside_package(self):
        bad = copy.deepcopy(self.manifest)
        bad["pages"][0]["wav_path"] = "../outside.wav"
        self.assertTrue(any("file unavailable or outside package" in e for e in self.errors(bad)))


if __name__ == "__main__":
    unittest.main()
