#!/usr/bin/env python3
"""Verify and copy external narration without awarding any review gate."""
import argparse
import hashlib
import json
import math
import shutil
import wave
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def confined_file(root, relative, label, errors):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        errors.append(f"{label}: relative file path required")
        return None
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        errors.append(f"{label}: file unavailable or outside package")
        return None
    return path


def checked_file(root, relative, expected, label, errors):
    path = confined_file(root, relative, label, errors)
    if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        errors.append(f"{label}: lowercase SHA-256 required")
    elif path and sha256(path) != expected:
        errors.append(f"{label}: SHA-256 mismatch")
    return path


def wav_measure(path):
    with wave.open(str(path), "rb") as wav:
        channels, width, rate, frames = wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
        if channels not in (1, 2) or width not in (1, 2, 3, 4) or not 8000 <= rate <= 192000 or frames <= 0:
            raise ValueError("unsupported or empty PCM WAV")
        samples = wav.readframes(frames)
        if len(samples) != frames * channels * width:
            raise ValueError("truncated PCM data")
        peak = 0
        square_sum = 0
        count = frames * channels
        for start in range(0, len(samples), width):
            sample = int.from_bytes(samples[start:start + width], "little", signed=width != 1)
            if width == 1:
                sample -= 128
            peak = max(peak, abs(sample))
            square_sum += sample * sample
        full_scale = 1 << (8 * width - 1)
        rms_dbfs = 20 * math.log10(max(math.sqrt(square_sum / count) / full_scale, 1e-12))
        if rms_dbfs < -55:
            raise ValueError("silent or near-silent PCM WAV")
        return {"sample_rate_hz": rate, "duration_s": round(frames / rate, 6),
                "channels": channels, "sample_width_bytes": width, "frame_count": frames,
                "peak_dbfs": round(20 * math.log10(max(peak / full_scale, 1e-12)), 2),
                "rms_dbfs": round(rms_dbfs, 2)}


def verify(manifest, package_dir, story_path):
    """Return (errors, measured pages, copied evidence paths); no subjective PASS."""
    errors, measured, files = [], [], {}
    package_dir = Path(package_dir).resolve()
    story_path = Path(story_path).resolve()
    story = json.loads(story_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "XHS-EXTERNAL-VOICE-V1":
        errors.append("schema_version: unsupported import contract")
    if manifest.get("story_sha256") != sha256(story_path):
        errors.append("story_sha256: frozen story mismatch")
    source = manifest.get("source")
    if not isinstance(source, dict) or any(not str(source.get(key, "")).strip()
                                               for key in ("provider", "voice", "source_uri", "license_name")):
        errors.append("source: provider, voice, source_uri and license_name required")
    rights = manifest.get("rights")
    if not isinstance(rights, dict):
        rights = {}
        errors.append("rights: audition and publication declarations required")
    for use in ("audition", "publication"):
        entry = rights.get(use)
        if not isinstance(entry, dict) or type(entry.get("allowed")) is not bool:
            errors.append(f"rights.{use}: explicit allowed boolean required")
            continue
        if not str(entry.get("scope", "")).strip():
            errors.append(f"rights.{use}: usage scope required")
        if entry["allowed"]:
            path = checked_file(package_dir, entry.get("evidence_path"), entry.get("evidence_sha256"),
                                f"rights.{use}", errors)
            if path:
                files[entry["evidence_path"]] = path
    if not isinstance(rights.get("audition"), dict) or rights["audition"].get("allowed") is not True:
        errors.append("rights.audition: audition use must be permitted before import")

    story_pages = [page for page in story["pages"] if page["role"] == "story"]
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        return errors + ["pages: at least one narrated story page required"], measured, files
    expected = {page["page"]: page for page in story_pages}
    seen = set()
    for index, page in enumerate(pages):
        label = f"pages[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{label}: object required")
            continue
        number = page.get("page")
        if type(number) is not int or number not in expected or number in seen:
            errors.append(f"{label}: unique story page number required")
            continue
        seen.add(number)
        if page.get("transcript") != expected[number]["english"]:
            errors.append(f"{label}: transcript must exactly match frozen English page text")
        if page.get("processing") != "none":
            errors.append(f"{label}: speed or time processing is not allowed")
        rel = page.get("wav_path")
        if not isinstance(rel, str) or Path(rel).suffix.lower() != ".wav":
            errors.append(f"{label}: PCM WAV path required")
        path = checked_file(package_dir, rel, page.get("sha256"), label, errors)
        if path:
            files[rel] = path
            try:
                actual = wav_measure(path)
                if page.get("sample_rate_hz") != actual["sample_rate_hz"]:
                    errors.append(f"{label}: sample rate differs from WAV")
                stated = page.get("duration_s")
                if isinstance(stated, bool) or not isinstance(stated, (int, float)) or not math.isfinite(stated) or abs(stated - actual["duration_s"]) > .03:
                    errors.append(f"{label}: duration differs from WAV")
                measured.append({"page": number, "wav_path": rel, "sha256": sha256(path), **actual})
            except (wave.Error, EOFError, ValueError) as exc:
                errors.append(f"{label}: invalid WAV: {exc}")
        audit = page.get("content_audit")
        if not isinstance(audit, dict) or audit.get("status") not in ("PENDING", "PASS"):
            errors.append(f"{label}: content_audit status PENDING or PASS required")
        elif audit["status"] == "PASS":
            if (not str(audit.get("reviewer", "")).strip() or audit.get("heard_exact_text") is not True
                    or audit.get("no_truncation") is not True or audit.get("natural_uncompressed_pace") is not True):
                errors.append(f"{label}: human text, ending and pace attestation required")
            proof = checked_file(package_dir, audit.get("evidence_path"), audit.get("evidence_sha256"),
                                 f"{label}.content_audit", errors)
            if proof:
                files[audit["evidence_path"]] = proof
    if [page.get("page") for page in pages if isinstance(page, dict)] != sorted(seen):
        errors.append("pages: imported story pages must be ordered and unique")
    if "source_manifest.json" in files or "import_report.json" in files:
        errors.append("file path conflicts with reserved import metadata name")
    return errors, measured, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--story", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    package = args.manifest.resolve().parent
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors, measured, files = verify(manifest, package, args.story)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}")
        raise SystemExit(1)
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit("BLOCKED: output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    for relative, source in files.items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if sha256(destination) != sha256(source):
            raise SystemExit(f"BLOCKED: copied file hash mismatch: {relative}")
    shutil.copyfile(args.manifest, output / "source_manifest.json")
    report = {"schema_version": "XHS-EXTERNAL-VOICE-IMPORT-REPORT-V1",
              "story_sha256": sha256(args.story), "source_manifest_sha256": sha256(args.manifest),
              "pages": measured, "audition_permission_declared": True,
              "publication_permission_declared": manifest["rights"]["publication"]["allowed"],
              "content_audit_complete": all(page["content_audit"]["status"] == "PASS" for page in manifest["pages"]),
              "voice_review": "BLOCKED_PENDING_USER_LISTENING", "timeline": "BLOCKED_PENDING_VOICE_REVIEW",
              "copyright_review": "BLOCKED_PENDING_RIGHTS_REVIEW", "publish_ready": "BLOCKED"}
    (output / "import_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"IMPORTED_FOR_REVIEW: {len(measured)} WAV(s); VOICE_REVIEW remains BLOCKED")


if __name__ == "__main__":
    main()
