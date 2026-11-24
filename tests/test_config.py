import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add app directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from utils import load_toml, save_toml, get_default_download_dir


class TestConfig(unittest.TestCase):
    def test_default_config_structure(self):
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            temp_path = Path(f.name)
        try:
            default_config = {
                "general": {
                    "current_preset": 0,
                    "current_quality": 0,
                    "path": get_default_download_dir(),
                    "global_args": "",
                    "update_ytdlp": True,
                },
                "presets": {
                    "best": "-f bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
                    "mp4": "-f bv*[vcodec^=avc]+ba[ext=m4a]/b",
                    "mp3": "--extract-audio --audio-format mp3 --audio-quality 0",
                },
            }
            save_toml(temp_path, default_config)
            loaded = load_toml(temp_path)
            self.assertIn("general", loaded)
            self.assertIn("presets", loaded)
            self.assertEqual(loaded["general"]["current_preset"], 0)
            self.assertTrue(loaded["general"]["update_ytdlp"])
            self.assertIn("best", loaded["presets"])
        finally:
            if temp_path.exists():
                temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
