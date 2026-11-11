"""Contract regressions for the story-first children's read-aloud route."""
import copy
import hashlib
import json
import re
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "skills/compact-storybook/read-aloud-v1"
sys.path.insert(0, str(SPEC))
from validate_read_aloud import load_contract, review_errors  # noqa: E402


class ReadAloudContractTest(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()
        self.review = json.loads((SPEC / "acceptance_template.json").read_text())

    def test_template_is_readable_and_initially_blocked(self):
        self.assertEqual(review_errors(self.review, ROOT, self.contract), [])
        self.assertTrue(all(x["status"] == "BLOCKED" for x in self.review["gates"].values()))
        self.assertEqual(self.review["timeline"]["pages"], [])

    def test_story_and_voice_precede_animation_and_timeline(self):
        ids = [stage["id"] for stage in self.contract["stages"]]
        self.assertLess(ids.index("STORY_REVIEW"), ids.index("READING_SCRIPT"))
        self.assertLess(ids.index("VOICE_REVIEW"), ids.index("TIMELINE"))
        self.assertLess(ids.index("TIMELINE"), ids.index("ANIMATION"))
        swapped = copy.deepcopy(self.review)
        swapped["stages"][0], swapped["stages"][6] = swapped["stages"][6], swapped["stages"][0]
        self.assertTrue(any("ordered workflow" in x for x in review_errors(swapped, ROOT, self.contract)))

    def test_unreviewed_animation_cannot_pass(self):
        review = copy.deepcopy(self.review)
        review["stages"][6]["status"] = "PASS"
        errors = review_errors(review, ROOT, self.contract)
        self.assertTrue(any("predecessor" in x for x in errors))
        self.assertTrue(any("PASS without evidence" in x for x in errors))

    def test_fixed_duration_and_unmeasured_timeline_are_rejected(self):
        review = copy.deepcopy(self.review)
        review["timeline"]["fixed_total_seconds"] = 33.3
        review["stages"][4]["status"] = "PASS"
        errors = review_errors(review, ROOT, self.contract)
        self.assertTrue(any("fixed_total_seconds" in x for x in errors))
        self.assertTrue(any("measured narration pages" in x for x in errors))

    def test_measured_approved_voice_can_define_timeline(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)

            def evidence(name, content=b"reviewed source evidence", kind="review"):
                path = base / name
                path.write_bytes(content)
                return {"path": name, "sha256": hashlib.sha256(content).hexdigest(),
                        "observation": "Checked the exact source and its content", "kind": kind}

            wav_path = base / "one.wav"
            with wave.open(str(wav_path), "wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(24000)
                out.writeframes(b"\0\0" * 24000)
            wav_evidence = evidence("one.wav", wav_path.read_bytes(), "audition")
            second_wav = evidence("two.wav", wav_path.read_bytes(), "audition")
            license_evidence = evidence("LICENSE.txt", b"sample model license record", "license")

            for i, stage in enumerate(self.review["stages"][:5]):
                stage["status"] = "PASS"
                stage["evidence"] = [evidence(f"stage{i}.txt")]
                if self.contract["stages"][i]["human_review"]:
                    stage["reviewer"] = {"type": "human", "name": "Named reviewer"}
            self.review["stages"][3]["evidence"] = [wav_evidence, second_wav, license_evidence]
            self.review["timeline"] = {"basis": "approved_narration_audio", "pages": [{
                "audio_approved": True, "audio_path": "one.wav", "audio_sha256": wav_evidence["sha256"],
                "voice_duration_s": 1.0, "lead_s": .2, "comprehension_hold_s": .8,
                "page_duration_s": 2.0, "turn_s": 0.0}], "total_duration_s": 2.0}
            self.assertEqual(review_errors(self.review, base, self.contract), [])
            self.review["timeline"]["pages"][0]["voice_duration_s"] = .5
            self.assertTrue(any("differ from WAV" in x for x in review_errors(self.review, base, self.contract)))

    def test_subjective_read_aloud_and_release_cannot_auto_pass(self):
        review = copy.deepcopy(self.review)
        review["read_aloud_checks"]["NARRATION_NATURAL"]["status"] = "PASS"
        review["gates"]["READ_ALOUD_PASS"]["status"] = "PASS"
        review["gates"]["PUBLISH_READY"]["status"] = "PASS"
        errors = review_errors(review, ROOT, self.contract)
        self.assertTrue(any("eight human criteria" in x for x in errors))
        self.assertTrue(any("named human reviewer" in x for x in errors))
        self.assertTrue(any("every other release gate" in x for x in errors))

    def test_observed_fail_needs_recorded_evidence(self):
        review = copy.deepcopy(self.review)
        review["read_aloud_checks"]["ENDING_QUALITY"]["status"] = "FAIL"
        self.assertTrue(any("FAIL without evidence" in x for x in review_errors(review, ROOT, self.contract)))

    def test_pilot_has_story_arc_but_no_premature_time_or_pass(self):
        pilot = ROOT / "research/xhs-read-aloud-v1/waiting-for-the-moon"
        story = json.loads((pilot / "story.json").read_text())
        body = [page for page in story["pages"] if page["role"] == "story"]
        words = sum(len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", page["english"])) for page in body)
        self.assertEqual(words, 91)
        self.assertEqual(len(story["pages"]), 8)
        self.assertEqual(story["beats"], ["hope_for_moon", "moon_absent", "rabbit_lonely",
                                          "stars_companion", "patient_wait", "moon_reveal", "safe_sleep"])
        self.assertFalse(any("duration_s" in page for page in story["pages"]))
        pilot_review = json.loads((pilot / "acceptance.json").read_text())
        self.assertEqual(review_errors(pilot_review, pilot, self.contract), [])
        self.assertEqual(pilot_review["gates"]["READ_ALOUD_PASS"]["status"], "BLOCKED")

    def test_new_document_links_resolve(self):
        documents = [ROOT / "AGENTS.md", ROOT / "CURRENT_WORKFLOW_STATUS.md",
                     SPEC / "WORKFLOW.md", ROOT / "research/xhs-read-aloud-v1/waiting-for-the-moon/STORY_AND_READING.md"]
        for document in documents:
            text = document.read_text()
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                local = (document.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(local.exists(), f"{document}: broken link {target}")
        self.assertIn("skills/compact-storybook/read-aloud-v1/WORKFLOW.md", (ROOT / "SKILL.md").read_text())
        self.assertIn("read-aloud-v1/WORKFLOW.md", (ROOT / "skills/compact-storybook/SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
