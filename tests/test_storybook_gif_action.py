"""Regression tests for the children's read-aloud GIF character-action gate."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("storybook_gif", ROOT / "scripts/export_storybook_gif.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class GifActionGateTests(unittest.TestCase):
    def make_frames(self, folder, move_subject):
        folder.mkdir()
        for i in range(5):
            image = Image.new("RGB", (120, 150), "#b2d2dc")
            pen = ImageDraw.Draw(image)
            delta = 3 * i if move_subject else 0
            pen.ellipse((38 + delta, 50, 68 + delta, 86), fill="white")
            # Scenery always moves; it must not be enough for action PASS.
            pen.ellipse((5 + i * 4, 6, 15 + i * 4, 16), fill="#f4dc8a")
            image.save(folder / f"{i:03}.png")

    def test_true_subject_change_produces_one_shot_gif(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_frames(root / "frames", True)
            report = module.export(root / "frames", root / "action.gif", (25, 40, 90, 100))
            self.assertEqual(report["frames"], 5)
            self.assertEqual(report["TECHNICAL_GIF_PASS"], "PASS")
            self.assertTrue(report["ACTION_PASS"].startswith("BLOCKED"))
            with Image.open(root / "action.gif") as gif:
                self.assertNotIn("loop", gif.info)
            self.assertTrue((root / "action.qa.json").exists())

    def test_background_motion_with_frozen_rabbit_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_frames(root / "frames", False)
            with self.assertRaisesRegex(ValueError, "static character"):
                module.export(root / "frames", root / "fail.gif", (25, 40, 90, 100))


if __name__ == "__main__":
    unittest.main()
