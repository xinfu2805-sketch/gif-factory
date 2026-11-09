import hashlib
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publish_gate
import stone_state


class StoneAuditTests(unittest.TestCase):
    def test_one_target_and_correct_state_order_but_missing_inbetweens(self):
        report = stone_state.audit()
        self.assertEqual(24, report['rendered_frames'])
        self.assertEqual(3, report['distinct_pose_assets'])
        self.assertTrue(report['target_unique_every_frame'])
        self.assertFalse(report['coordinate_continuity_pass'])
        self.assertEqual([5, 9], [int(v.split(':')[0].split('_')[1]) for v in report['violations']])
        self.assertEqual('GROUND', report['frames'][0]['stage'])
        self.assertEqual('BEAK_CONTACT', report['frames'][3]['stage'])
        self.assertEqual('SUNK', report['frames'][23]['stage'])
        self.assertEqual(1175, report['frames'][18]['water_top_px'])
        self.assertLess(report['frames'][23]['water_top_px'], 1175)

    def test_out_of_range_frame_rejected(self):
        with self.assertRaises(ValueError):
            stone_state.frame_state(24)


class PublishGateTests(unittest.TestCase):
    def test_pilot_technical_pass_cannot_be_publish_ready(self):
        report = publish_gate.evaluate('pilot')
        self.assertEqual('PASS', report['status']['TECHNICAL_PASS'])
        self.assertEqual('BLOCKED', report['status']['ACTION_PASS'])
        self.assertEqual('BLOCKED', report['status']['AUDIO_PASS'])
        self.assertEqual('BLOCKED', report['status']['PUBLISH_READY'])

    def test_missing_full_video_has_separate_blocked_gate(self):
        report = publish_gate.evaluate('full')
        self.assertEqual('BLOCKED', report['status']['TECHNICAL_PASS'])
        self.assertEqual('BLOCKED', report['status']['PUBLISH_READY'])

    def test_filled_review_fields_without_matching_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'proof.txt').write_text('reviewed')
            record = {'decision': 'PASS', 'reviewer': 'Example', 'reviewed_at': '2026-11-09',
                      'observations': 'looks okay', 'reviewed_media_sha256': 'media-hash',
                      'evidence_file': 'proof.txt', 'evidence_sha256': 'wrong-hash'}
            self.assertFalse(publish_gate.signed_review(record, 'media-hash', root))
            record['evidence_sha256'] = hashlib.sha256((root / 'proof.txt').read_bytes()).hexdigest()
            self.assertTrue(publish_gate.signed_review(record, 'media-hash', root))
            self.assertFalse(publish_gate.signed_review(record, 'other-media-hash', root))
            self.assertIsNone(publish_gate.local_file('../proof.txt', root))

    def test_audio_fields_and_test_music_cannot_sign_pass(self):
        self.assertFalse(publish_gate.formal_music_allowed(
            {'formal_background_music': True, 'approved_use': True,
             'source_type': 'original_composition'}, Path('music-pipeline-test.wav')))
        self.assertFalse(publish_gate.formal_music_allowed(
            {'formal_background_music': False, 'approved_use': True,
             'source_type': 'original_composition'}, Path('music.wav')))
        with tempfile.TemporaryDirectory() as tmp:
            renamed = Path(tmp) / 'renamed.wav'
            renamed.write_bytes((publish_gate.ROOT / 'output/music-pipeline-test.wav').read_bytes())
            self.assertFalse(publish_gate.formal_music_allowed(
                {'formal_background_music': True, 'approved_use': True,
                 'source_type': 'original_composition'}, renamed))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'proof.txt').write_text('audition')
            record = {'decision': 'PASS', 'reviewer': 'Example', 'reviewed_at': '2026-11-09',
                      'observations': 'heard mix', 'reviewed_media_sha256': 'media-hash',
                      'evidence_file': 'proof.txt',
                      'evidence_sha256': hashlib.sha256((root / 'proof.txt').read_bytes()).hexdigest(),
                      'voice_auditions': [], 'tracks': {}}
            self.assertFalse(publish_gate.audio_approved(record, 'media-hash', root))
            self.assertFalse(publish_gate.audio_approved(record, 'media-hash', root, full=True))

    def test_two_existing_voice_files_without_listening_do_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'proof.txt').write_text('review evidence')
            auditions = []
            for i in range(2):
                path = root / f'voice-{i}.wav'
                with wave.open(str(path), 'wb') as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(24000)
                    wav.writeframes(bytes([i, 0]) * (24000 * 9))
                auditions.append({'file': path.name, 'sha256': publish_gate.sha256(path),
                                  'listening_review': {}})
            record = {'decision': 'PASS', 'reviewer': 'Example', 'reviewed_at': '2026-11-09',
                      'observations': 'field was filled', 'reviewed_media_sha256': 'media-hash',
                      'evidence_file': 'proof.txt',
                      'evidence_sha256': publish_gate.sha256(root / 'proof.txt'),
                      'voice_auditions': auditions, 'tracks': {}}
            self.assertFalse(publish_gate.audio_approved(record, 'media-hash', root))


if __name__ == '__main__':
    unittest.main()
