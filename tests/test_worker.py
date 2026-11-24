import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add app directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from worker import DownloadWorker


class TestDownloadWorker(unittest.TestCase):
    def setUp(self):
        self.mock_item = MagicMock()
        self.mock_item.data.return_value = 0
        self.config = {
            "general": {
                "current_preset": 0,
                "current_quality": 0,
                "path": "C:/Downloads",
                "global_args": "",
                "update_ytdlp": True,
            },
            "presets": {
                "best": "-f bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
                "mp4": "-f bv*[vcodec^=avc]+ba[ext=m4a]/b",
                "mp3": "--extract-audio --audio-format mp3 --audio-quality 0",
            },
        }

    def test_build_command_best(self):
        worker = DownloadWorker(
            self.mock_item,
            self.config,
            "https://www.youtube.com/watch?v=123",
            "C:/Downloads",
            "best",
            "Best",
        )
        cmd = worker.command
        self.assertIn("-N", cmd)
        self.assertIn("8", cmd)
        self.assertIn("--buffer-size", cmd)
        self.assertIn("1024k", cmd)
        self.assertIn("--http-chunk-size", cmd)
        self.assertIn("10M", cmd)
        self.assertIn("--no-mtime", cmd)
        self.assertIn("-P", cmd)
        self.assertIn("C:/Downloads", cmd)
        self.assertIn("--", cmd)
        self.assertIn("https://www.youtube.com/watch?v=123", cmd)
        # "Best" should not inject -S res:...
        self.assertNotIn("-S", cmd)

    def test_build_command_quality_1080p(self):
        worker = DownloadWorker(
            self.mock_item,
            self.config,
            "https://www.youtube.com/watch?v=123",
            "C:/Downloads",
            "best",
            "1080p",
        )
        cmd = worker.command
        self.assertIn("-S", cmd)
        self.assertIn("res:1080", cmd)

    def test_build_command_audio_preset_skips_resolution(self):
        worker = DownloadWorker(
            self.mock_item,
            self.config,
            "https://www.youtube.com/watch?v=123",
            "C:/Downloads",
            "mp3",
            "1080p",  # audio preset should ignore video resolution
        )
        cmd = worker.command
        self.assertNotIn("res:1080", cmd)
        self.assertIn("--extract-audio", cmd)

    def test_build_command_with_global_args(self):
        config_with_args = dict(self.config)
        config_with_args["general"]["global_args"] = "--geo-bypass"
        worker = DownloadWorker(
            self.mock_item,
            config_with_args,
            "https://www.youtube.com/watch?v=123",
            "C:/Downloads",
            "best",
            "Best",
        )
        cmd = worker.command
        self.assertIn("--geo-bypass", cmd)


if __name__ == "__main__":
    unittest.main()
