#!/usr/bin/env python3
"""Validate a read-aloud review record without awarding subjective PASSes."""
import argparse
import hashlib
import json
import math
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALID = {"PASS", "FAIL", "BLOCKED"}


def load_contract():
    return json.loads((HERE / "workflow_contract.json").read_text())


def review_errors(review, root, contract=None):
    contract = contract or load_contract()
    root = Path(root).resolve()
    errors = []

    def evidence_file(item, label):
        rel = item.get("path") if isinstance(item, dict) else None
        digest = item.get("sha256") if isinstance(item, dict) else None
        observation = item.get("observation") if isinstance(item, dict) else None
        if not isinstance(rel, str) or not rel or not isinstance(digest, str) or len(digest) != 64:
            errors.append(f"{label}: evidence needs relative path and SHA-256")
            return None
        if not isinstance(observation, str) or len(observation.strip()) < 12:
            errors.append(f"{label}: evidence needs a specific observation")
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(f"{label}: evidence file unavailable: {rel}")
            return None
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f"{label}: evidence SHA-256 mismatch: {rel}")
        return path

    def checked_decision(value, label, human=False):
        if not isinstance(value, dict):
            errors.append(f"{label}: decision must be an object")
            return "BLOCKED"
        status = value.get("status")
        if status not in VALID:
            errors.append(f"{label}: invalid status {status!r}")
            return "BLOCKED"
        evidence = value.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{label}: evidence must be a list")
            evidence = []
        if status in ("PASS", "FAIL") and not evidence:
            errors.append(f"{label}: {status} without evidence")
        for i, item in enumerate(evidence):
            evidence_file(item, f"{label}.evidence[{i}]")
        if status == "PASS" and human:
            reviewer = value.get("reviewer")
            if not isinstance(reviewer, dict) or reviewer.get("type") != "human" or not str(reviewer.get("name", "")).strip():
                errors.append(f"{label}: human PASS needs named human reviewer")
        return status

    if review.get("workflow_version") != contract["version"]:
        errors.append("workflow_version does not match contract")
    ids = [s["id"] for s in contract["stages"]]
    stages = review.get("stages")
    if not isinstance(stages, list) or [s.get("id") for s in stages if isinstance(s, dict)] != ids:
        errors.append("stages must match the ordered workflow contract")
        stages = []
    stage_status = {}
    for i, stage in enumerate(stages):
        spec = contract["stages"][i]
        status = checked_decision(stage, f"stages.{spec['id']}", spec["human_review"])
        stage_status[spec["id"]] = status
        if status == "PASS" and any(stage_status.get(previous) != "PASS" for previous in ids[:i]):
            errors.append(f"stages.{spec['id']}: predecessor has not PASSed")
        if spec["id"] == "VOICE_REVIEW" and status == "PASS":
            items = stage.get("evidence", [])
            wav_count = 0
            for item in items:
                if not isinstance(item, dict) or not str(item.get("path", "")).lower().endswith(".wav"):
                    continue
                path = (root / item["path"]).resolve()
                if not path.is_relative_to(root) or not path.is_file():
                    continue
                try:
                    with wave.open(str(path)) as wav:
                        if wav.getnframes() > 0 and wav.getframerate() > 0:
                            wav_count += 1
                except wave.Error:
                    errors.append(f"stages.VOICE_REVIEW: invalid WAV audition {item['path']}")
            license_count = sum(item.get("kind") == "license" for item in items if isinstance(item, dict))
            if wav_count < 2 or license_count < 1:
                errors.append("stages.VOICE_REVIEW: two WAV auditions and license evidence required")

    timeline = review.get("timeline")
    if not isinstance(timeline, dict) or timeline.get("basis") != contract["timeline_basis"]:
        errors.append("timeline must be based on approved narration audio")
        timeline = {}
    if "fixed_total_seconds" in timeline:
        errors.append("timeline cannot impose fixed_total_seconds")
    if stage_status.get("TIMELINE") == "PASS":
        if stage_status.get("VOICE_REVIEW") != "PASS":
            errors.append("TIMELINE cannot PASS before VOICE_REVIEW")
        pages = timeline.get("pages")
        if not isinstance(pages, list) or not pages:
            errors.append("TIMELINE PASS requires measured narration pages")
        else:
            total = 0.0
            story_pages = 0
            for i, page in enumerate(pages):
                label = f"timeline.pages[{i}]"
                if not isinstance(page, dict):
                    errors.append(f"{label}: page must be an object")
                    continue
                role = page.get("role")
                if role == "cover":
                    if i != 0:
                        errors.append(f"{label}: silent cover must be page 0")
                    if any(key in page for key in ("audio_approved", "audio_path", "audio_sha256", "voice_duration_s", "voice_review")):
                        errors.append(f"{label}: silent cover cannot claim narration fields")
                    cover_review = page.get("cover_review")
                    if checked_decision(cover_review, f"{label}.cover_review", True) != "PASS":
                        errors.append(f"{label}: silent cover display and turn need human approval")
                    items = cover_review.get("evidence", []) if isinstance(cover_review, dict) else []
                    if not any(isinstance(item, dict) and item.get("kind") == "timing_approval" for item in items):
                        errors.append(f"{label}: cover timing approval evidence required")
                    try:
                        duration = float(page["display_duration_s"])
                        turn = float(page["turn_s"])
                        if not math.isfinite(duration) or not math.isfinite(turn) or duration <= 0 or turn <= 0:
                            errors.append(f"{label}: cover display and turn must be positive measured decisions")
                        approved_display = float(cover_review["approved_display_duration_s"])
                        approved_turn = float(cover_review["approved_turn_s"])
                        if (not math.isfinite(approved_display) or not math.isfinite(approved_turn) or
                            abs(approved_display - duration) > .01 or abs(approved_turn - turn) > .01):
                            errors.append(f"{label}: human cover review must approve these exact display and turn seconds")
                        total += duration + turn
                    except (KeyError, TypeError, ValueError):
                        errors.append(f"{label}: approved cover display_duration_s and turn_s required")
                    continue
                if role != "story":
                    errors.append(f"{label}: role must be cover or story")
                    continue
                story_pages += 1
                if page.get("audio_approved") is not True:
                    errors.append(f"{label}: approved narration clip required")
                voice_review = page.get("voice_review")
                if checked_decision(voice_review, f"{label}.voice_review", True) != "PASS":
                    errors.append(f"{label}: story narration needs human voice approval")
                if not isinstance(voice_review, dict) or voice_review.get("approved_audio_sha256") != page.get("audio_sha256"):
                    errors.append(f"{label}: voice approval must bind to this WAV SHA-256")
                items = voice_review.get("evidence", []) if isinstance(voice_review, dict) else []
                if not any(isinstance(item, dict) and item.get("kind") == "voice_approval" for item in items):
                    errors.append(f"{label}: voice approval evidence required")
                path = evidence_file({"path": page.get("audio_path"), "sha256": page.get("audio_sha256"),
                                      "observation": "Measured approved narration audio clip"}, label)
                if path and path.suffix.lower() != ".wav":
                    errors.append(f"{label}: story narration must be a real WAV")
                try:
                    voice = float(page["voice_duration_s"])
                    lead = float(page["lead_s"])
                    hold = float(page["comprehension_hold_s"])
                    duration = float(page["page_duration_s"])
                    turn = float(page["turn_s"])
                    if not all(math.isfinite(v) for v in (voice, lead, hold, duration, turn)):
                        raise ValueError("nonfinite duration")
                    if voice <= 0 or lead < 0 or hold < .5 or turn < 0 or duration + .03 < lead + voice + hold:
                        errors.append(f"{label}: page time must cover natural voice and comprehension hold")
                    if i == len(pages) - 1 and turn != 0:
                        errors.append(f"{label}: final page cannot turn after ending")
                    total += duration + turn
                    if path and path.suffix.lower() == ".wav":
                        with wave.open(str(path)) as wav:
                            measured = wav.getnframes() / wav.getframerate()
                        if abs(measured - voice) > .03:
                            errors.append(f"{label}: stated voice seconds differ from WAV")
                except (KeyError, TypeError, ValueError, wave.Error) as exc:
                    errors.append(f"{label}: invalid timing or WAV: {exc}")
            if story_pages == 0:
                errors.append("TIMELINE PASS requires at least one narrated story page")
            try:
                if abs(float(timeline["total_duration_s"]) - total) > .05:
                    errors.append("timeline total must equal the page and turn sum")
            except (KeyError, TypeError, ValueError):
                errors.append("timeline total_duration_s required after voice timing")

    checks = review.get("read_aloud_checks")
    if not isinstance(checks, dict) or list(checks) != contract["read_aloud_criteria"]:
        errors.append("read_aloud_checks must contain all eight ordered criteria")
        checks = {}
    check_status = {key: checked_decision(value, f"read_aloud_checks.{key}", True)
                    for key, value in checks.items() if key in contract["read_aloud_criteria"]}

    gates = review.get("gates")
    if not isinstance(gates, dict) or list(gates) != contract["release_gates"]:
        errors.append("gates must match the ordered release gate list")
        gates = {}
    gate_status = {key: checked_decision(value, f"gates.{key}", key in contract["human_gates"])
                   for key, value in gates.items() if key in contract["release_gates"]}
    if gate_status.get("READ_ALOUD_PASS") == "PASS":
        if any(check_status.get(key) != "PASS" for key in contract["read_aloud_criteria"]):
            errors.append("READ_ALOUD_PASS requires all eight human criteria PASS")
        if any(stage_status.get(key) != "PASS" for key in ("STORY_REVIEW", "VOICE_REVIEW", "TIMELINE", "FULL_AV_REVIEW")):
            errors.append("READ_ALOUD_PASS requires reviewed story, voice, timing and full audiovisual evidence")
    if gate_status.get("PUBLISH_READY") == "PASS":
        if any(gate_status.get(key) != "PASS" for key in contract["release_gates"] if key != "PUBLISH_READY"):
            errors.append("PUBLISH_READY requires every other release gate PASS")
        if stage_status.get("EXPORT") != "PASS":
            errors.append("PUBLISH_READY requires completed EXPORT")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("review", type=Path)
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    review = json.loads(args.review.read_text())
    errors = review_errors(review, args.root or args.review.parent)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("CONTRACT_VALID: recorded PASSes are evidence-backed; no subjective gate was signed automatically")


if __name__ == "__main__":
    main()
