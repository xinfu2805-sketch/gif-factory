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
            story_source = base / "story.json"
            story_source.write_text(json.dumps({"pages": [{"page": 0, "role": "story"}]}))
            story_sha = hashlib.sha256(story_source.read_bytes()).hexdigest()
            self.review["timeline"] = {"basis": "approved_narration_audio", "story_sha256": story_sha,
                                       "pages": [{
                "page": 0, "role": "story",
                "audio_approved": True, "audio_path": "one.wav", "audio_sha256": wav_evidence["sha256"],
                "voice_review": {"status": "PASS", "approved_audio_sha256": wav_evidence["sha256"],
                                 "evidence": [evidence("voice_approved.txt", kind="voice_approval")],
                                 "reviewer": {"type": "human", "name": "Named reviewer"}},
                "voice_duration_s": 1.0, "lead_s": .2, "comprehension_hold_s": .8,
                "page_duration_s": 2.0, "turn_s": 0.0}], "total_duration_s": 2.0}
            self.assertEqual(review_errors(self.review, base, self.contract), [])
            self.review["timeline"]["pages"][0]["voice_duration_s"] = .5
            self.assertTrue(any("differ from WAV" in x for x in review_errors(self.review, base, self.contract)))

    def test_reviewed_silent_cover_then_narrated_story_is_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)

            def evidence(name, kind, content=b"specific review evidence for this page"):
                path = base / name
                path.write_bytes(content)
                return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "observation": "Checked this exact page and its timing", "kind": kind}

            with wave.open(str(base / "story.wav"), "wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(24000)
                out.writeframes(b"\0\0" * 24000)
            wav_sha = hashlib.sha256((base / "story.wav").read_bytes()).hexdigest()
            for i, stage in enumerate(self.review["stages"][:5]):
                stage["status"] = "PASS"
                stage["evidence"] = [evidence(f"stage{i}.txt", "review")]
                if self.contract["stages"][i]["human_review"]:
                    stage["reviewer"] = {"type": "human", "name": "Named reviewer"}
            wav_bytes = (base / "story.wav").read_bytes()
            self.review["stages"][3]["evidence"] = [
                evidence("first.wav", "audition", wav_bytes), evidence("second.wav", "audition", wav_bytes),
                evidence("license.txt", "license")]
            story_source = base / "story.json"
            story_source.write_text(json.dumps({"pages": [{"page": 0, "role": "cover"},
                                                          {"page": 1, "role": "story"}]}))
            story_sha = hashlib.sha256(story_source.read_bytes()).hexdigest()
            cover = {"page": 0, "role": "cover", "display_duration_s": 2.4, "turn_s": .5,
                     "cover_review": {"status": "PASS", "approved_display_duration_s": 2.4,
                                      "approved_turn_s": .5,
                                      "evidence": [evidence("cover-timing.txt", "timing_approval")],
                                      "reviewer": {"type": "human", "name": "Named reviewer"}}}
            story = {"page": 1, "role": "story", "audio_approved": True, "audio_path": "story.wav",
                     "audio_sha256": wav_sha, "voice_duration_s": 1.0, "lead_s": .2,
                     "comprehension_hold_s": .8, "page_duration_s": 2.0, "turn_s": 0.0,
                     "voice_review": {"status": "PASS", "approved_audio_sha256": wav_sha,
                                      "evidence": [evidence("story-voice.txt", "voice_approval")],
                                      "reviewer": {"type": "human", "name": "Named reviewer"}}}
            self.review["timeline"] = {"basis": "approved_narration_audio", "story_sha256": story_sha,
                                       "pages": [cover, story],
                                       "total_duration_s": 4.9}
            self.assertEqual(review_errors(self.review, base, self.contract), [])

            wrong_cover_approval = copy.deepcopy(self.review)
            wrong_cover_approval["timeline"]["pages"][0]["cover_review"]["approved_turn_s"] = .3
            self.assertTrue(any("approve these exact display and turn" in x
                                for x in review_errors(wrong_cover_approval, base, self.contract)))
            wrong_cover_approval["timeline"]["pages"][0]["cover_review"]["approved_turn_s"] = float("nan")
            self.assertTrue(any("approve these exact display and turn" in x
                                for x in review_errors(wrong_cover_approval, base, self.contract)))

            no_voice = copy.deepcopy(self.review)
            no_voice["timeline"]["pages"][1].pop("audio_path")
            no_voice["timeline"]["pages"][1].pop("audio_sha256")
            no_voice["timeline"]["pages"][1]["audio_approved"] = False
            errors = review_errors(no_voice, base, self.contract)
            self.assertTrue(any("approved narration clip required" in x for x in errors))
            self.assertTrue(any("evidence needs relative path and SHA-256" in x for x in errors))

            false_cover = copy.deepcopy(self.review)
            false_cover["timeline"]["pages"][1] = copy.deepcopy(cover)
            self.assertTrue(any("silent cover must be page 0" in x for x in review_errors(false_cover, base, self.contract)))

    def _mapping_errors(self, page_specs):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            story = {"pages": [{"page": 0, "role": "cover"}, {"page": 1, "role": "story"},
                               {"page": 2, "role": "story"}]}
            source = base / "story.json"
            source.write_text(json.dumps(story))
            review = copy.deepcopy(self.review)
            review["stages"][4]["status"] = "PASS"
            review["timeline"] = {"basis": "approved_narration_audio",
                                  "story_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                  "pages": [{"page": number, "role": role} for number, role in page_specs],
                                  "total_duration_s": 0.0}
            return review_errors(review, base, self.contract)

    def test_missing_story_page_blocks_timeline(self):
        errors = self._mapping_errors([(0, "cover"), (2, "story")])
        self.assertTrue(any("page count differs from story.json" in x for x in errors))

    def test_duplicate_story_page_blocks_timeline(self):
        errors = self._mapping_errors([(0, "cover"), (1, "story"), (1, "story")])
        self.assertTrue(any("duplicate page numbers" in x for x in errors))

    def test_reordered_story_pages_block_timeline(self):
        errors = self._mapping_errors([(0, "cover"), (2, "story"), (1, "story")])
        self.assertTrue(any("order differ from story.json" in x for x in errors))

    def test_page_role_mismatch_blocks_timeline(self):
        errors = self._mapping_errors([(0, "cover"), (1, "cover"), (2, "story")])
        self.assertTrue(any("role differs from story.json" in x for x in errors))

    def test_story_page_without_narration_is_blocked(self):
        review = copy.deepcopy(self.review)
        review["stages"][4]["status"] = "PASS"
        review["timeline"] = {"basis": "approved_narration_audio", "pages": [{
            "role": "story", "audio_approved": False, "lead_s": .2,
            "comprehension_hold_s": .8, "page_duration_s": 2.0, "turn_s": 0.0,
            "voice_review": {"status": "BLOCKED", "evidence": [], "reviewer": None}}],
            "total_duration_s": 2.0}
        errors = review_errors(review, ROOT, self.contract)
        self.assertTrue(any("approved narration clip required" in x for x in errors))
        self.assertTrue(any("story narration needs human voice approval" in x for x in errors))
        self.assertTrue(any("evidence needs relative path and SHA-256" in x for x in errors))

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
        words = sum(len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", page["english"])) for page in body)
        doc = (pilot / "STORY_AND_READING.md").read_text()
        documented = re.search(r"\*\*English body word count: (\d+)\.\*\*", doc)
        self.assertIsNotNone(documented)
        self.assertEqual(words, story["english_body_word_count"])
        self.assertEqual(words, int(documented.group(1)))
        self.assertEqual(len(story["pages"]), 8)
        for page in story["pages"]:
            self.assertIn(page["english"], doc)
            self.assertIn(page["chinese"], doc)
        self.assertEqual(story["pages"][2]["english"], "The sky grew darker, but the moon was nowhere to be seen. The rabbit waited.")
        self.assertEqual(story["pages"][3]["english"], "A big cloud was hiding the moon. The rabbit’s ears drooped. It felt a little lonely.")
        self.assertEqual(story["pages"][6]["english"], "At last, the cloud drifted away. The round moon appeared, glowing softly above the hill.")
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
