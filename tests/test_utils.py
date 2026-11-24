import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add app directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from utils import (
    BIN_DIR,
    LEGACY_BIN_DIR,
    QUALITY_OPTIONS,
    get_bin_dirs,
    get_default_download_dir,
    get_ffmpeg_dir,
    get_ytdlp_path,
    load_toml,
    save_toml,
)


class TestUtils(unittest.TestCase):
    def test_bin_dirs(self):
        dirs = get_bin_dirs()
        self.assertIsInstance(dirs, list)
        self.assertIn(BIN_DIR, dirs)
        self.assertIn(LEGACY_BIN_DIR, dirs)

    def test_get_ytdlp_path(self):
        path = get_ytdlp_path()
        self.assertIsInstance(path, str)
        self.assertTrue(len(path) > 0)
        self.assertTrue("yt-dlp" in path.lower())

    def test_get_ffmpeg_dir(self):
        # Should not raise exception
        ffmpeg_dir = get_ffmpeg_dir()
        if ffmpeg_dir is not None:
            self.assertIsInstance(ffmpeg_dir, Path)

    def test_get_default_download_dir(self):
        d = get_default_download_dir()
        self.assertIsInstance(d, str)
        self.assertTrue(Path(d).exists())

    def test_quality_options(self):
        self.assertIn("Best", QUALITY_OPTIONS)
        self.assertIn("1080p", QUALITY_OPTIONS)
        self.assertIn("720p", QUALITY_OPTIONS)
        self.assertIn("480p", QUALITY_OPTIONS)

    def test_toml_roundtrip(self):
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            temp_path = Path(f.name)
        try:
            data = {"test_section": {"key": "value", "number": 42}}
            save_toml(temp_path, data)
            loaded = load_toml(temp_path)
            self.assertEqual(loaded["test_section"]["key"], "value")
            self.assertEqual(loaded["test_section"]["number"], 42)
        finally:
            if temp_path.exists():
                temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
