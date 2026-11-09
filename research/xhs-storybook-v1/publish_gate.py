#!/usr/bin/env python3
"""Hash-bound technical and director gates; a pilot can never be publish-ready."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
KEYS = ('TECHNICAL_PASS', 'VISUAL_PASS', 'ACTION_PASS', 'AUDIO_PASS', 'EDITORIAL_PASS')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(relative, root=ROOT):
    if not isinstance(relative, str) or not relative:
        return None
    path = (root / relative).resolve()
    return path if path.is_relative_to(root.resolve()) and path.is_file() else None


def bound_file(record, expected_sha=None, root=ROOT):
    if not isinstance(record, dict):
        return None
    path = local_file(record.get('file'), root)
    if not path:
        return None
    actual = sha256(path)
    return path if record.get('sha256') == actual and (expected_sha is None or actual == expected_sha) else None


def signed_review(record, media_sha, root=ROOT):
    if not isinstance(record, dict):
        return False
    evidence = bound_file({'file': record.get('evidence_file'), 'sha256': record.get('evidence_sha256')}, root=root)
    return bool(record.get('decision') == 'PASS' and record.get('reviewer')
                and record.get('reviewed_media_sha256') == media_sha
                and record.get('reviewed_at') and record.get('observations') and evidence)


def command(*args):
    return subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def probe_media(path, expected):
    if not path or not path.is_file():
        return 'BLOCKED', {'reason': 'media_missing'}
    try:
        data = json.loads(command('ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(path)).stdout)
        video = next(s for s in data['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in data['streams'] if s['codec_type'] == 'audio')
        levels = command('ffmpeg', '-hide_banner', '-i', str(path), '-vn', '-af', 'volumedetect', '-f', 'null', '-').stderr
        peak = re.findall(r'max_volume: ([^ ]+) dB', levels)
        decoded = command('ffmpeg', '-v', 'error', '-i', str(path), '-f', 'null', '-')
        observed = {'width': video['width'], 'height': video['height'], 'fps': video['avg_frame_rate'],
                    'frames': int(video['nb_read_frames']), 'duration': float(data['format']['duration']),
                    'audio_codec': audio['codec_name'], 'audio_duration': float(audio['duration']),
                    'audio_start': float(audio.get('start_time', 0)), 'video_start': float(video.get('start_time', 0)),
                    'audio_peak_dbfs': float(peak[-1]) if peak else None, 'decode_errors': decoded.stderr.strip()}
        ok = (observed['width'] == 1080 and observed['height'] == 1920 and observed['fps'] == '6/1'
              and observed['frames'] == expected['frames'] and abs(observed['duration'] - expected['duration']) < .03
              and observed['audio_codec'] == 'aac' and abs(observed['audio_duration'] - expected['duration']) < .05
              and abs(observed['audio_start'] - observed['video_start']) < .02
              and observed['audio_peak_dbfs'] is not None and observed['audio_peak_dbfs'] > -50
              and not observed['decode_errors'])
        return ('PASS' if ok else 'FAIL'), observed
    except (subprocess.CalledProcessError, KeyError, ValueError, StopIteration, IndexError) as exc:
        return 'FAIL', {'reason': f'probe_or_decode_failed: {exc}'}


def duration_seconds(path):
    try:
        data = json.loads(command('ffprobe', '-v', 'error', '-show_format', '-of', 'json', str(path)).stdout)
        return float(data['format']['duration'])
    except (subprocess.CalledProcessError, KeyError, ValueError):
        return None


def formal_music_allowed(item, path):
    known_test = ROOT / 'output/music-pipeline-test.wav'
    return bool(item.get('formal_background_music') is True
                and item.get('approved_use') is True
                and item.get('source_type') in {'original_recording', 'licensed_music', 'original_composition'}
                and 'pipeline-test' not in path.name
                and (not known_test.is_file() or sha256(path) != sha256(known_test)))


def audio_approved(review, video_sha, root=ROOT, full=False):
    if not signed_review(review, video_sha, root):
        return False
    auditions = review.get('voice_auditions', [])
    if not isinstance(auditions, list) or len(auditions) != 2:
        return False
    voices = [bound_file(v, root=root) for v in auditions]
    if not all(voices) or sha256(voices[0]) == sha256(voices[1]):
        return False
    if not all(8 <= (duration_seconds(v) or 0) <= 10 for v in voices):
        return False
    if not all(signed_review(v.get('listening_review'), sha256(path), root) for v, path in zip(auditions, voices)):
        return False
    tracks = review.get('tracks', {})
    if not isinstance(tracks, dict) or set(tracks) != {'narration', 'music', 'foley'}:
        return False
    track_hashes = {}
    for name, item in tracks.items():
        path = bound_file(item, root=root)
        rights = bound_file(item.get('rights_evidence'), root=root) if isinstance(item, dict) else None
        if not path or not rights or not signed_review(item.get('listening_review'), sha256(path), root):
            return False
        if item.get('approved_use') is not True or item.get('source_type') not in {'original_recording', 'licensed_model', 'licensed_music', 'original_composition'}:
            return False
        if name == 'music' and not formal_music_allowed(item, path):
            return False
        track_hashes[name] = sha256(path)
    if not signed_review(review.get('final_mix_listening_review'), video_sha, root):
        return False
    if full:
        manifest_path = bound_file(review.get('mix_manifest'), root=root)
        if not manifest_path:
            return False
        try:
            manifest = json.loads(manifest_path.read_text())
        except (ValueError, UnicodeError):
            return False
        if manifest.get('video_sha256') != video_sha or manifest.get('stems_sha256') != track_hashes or manifest.get('contains_approved_narration_music_foley') is not True:
            return False
    return True


def evaluate(scope, root=ROOT):
    decisions = json.loads((root / 'review/director-decisions.json').read_text())
    if scope == 'pilot':
        video = root / 'output/crow-action-pilot.mp4'
        expected = {'duration': 4, 'frames': 24}
    else:
        spec_path = root / 'review/full-spec.json'
        if spec_path.is_file():
            spec = json.loads(spec_path.read_text())
            video = local_file(spec.get('video'), root)
            expected = {'duration': spec['duration'], 'frames': spec['frames']}
        else:
            video, expected = None, {'duration': 0, 'frames': 0}
    technical, observed = probe_media(video, expected)
    video_sha = sha256(video) if video and video.is_file() else None
    result = {'TECHNICAL_PASS': technical}
    for key in ('VISUAL_PASS', 'ACTION_PASS', 'EDITORIAL_PASS'):
        result[key] = 'PASS' if video_sha and signed_review(decisions.get(key), video_sha, root) else 'BLOCKED'
    stone_audit_path = root / 'review/stone-audit.json'
    stone_audit = json.loads(stone_audit_path.read_text()) if stone_audit_path.is_file() else None
    if scope == 'pilot' and (not stone_audit or stone_audit.get('video_sha256') != video_sha or not stone_audit.get('target_unique_every_frame') or not stone_audit.get('coordinate_continuity_pass') or stone_audit.get('distinct_pose_assets', 0) < 4):
        result['ACTION_PASS'] = 'BLOCKED'
    if scope == 'full' and not decisions.get('ACTION_PASS', {}).get('full_action_review_complete'):
        result['ACTION_PASS'] = 'BLOCKED'
    result['AUDIO_PASS'] = 'PASS' if video_sha and audio_approved(decisions.get('AUDIO_PASS'), video_sha, root, full=scope == 'full') else 'BLOCKED'
    if scope == 'full':
        editorial = decisions.get('EDITORIAL_PASS', {})
        if not all(local_file(editorial.get(key), root) for key in ('cover_file', 'note_file', 'rights_ledger')):
            result['EDITORIAL_PASS'] = 'BLOCKED'
    result['PUBLISH_READY'] = ('PASS' if scope == 'full' and all(result[k] == 'PASS' for k in KEYS) else 'BLOCKED')
    return {'scope': scope, 'status': result, 'video_sha256': video_sha,
            'objective': observed, 'action_audit': stone_audit if scope == 'pilot' else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=['pilot', 'full'], default='pilot')
    args = parser.parse_args()
    result = evaluate(args.scope)
    target = ROOT / f'review/acceptance-{args.scope}.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if args.scope == 'pilot':
        (ROOT / 'review/acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['status'], ensure_ascii=False, indent=2))
    raise SystemExit(1 if result['status']['TECHNICAL_PASS'] == 'FAIL' else 0)


if __name__ == '__main__':
    main()
