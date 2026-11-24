import sys
import unittest
from pathlib import Path

# Add app directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from playlist_dialog import (
    clean_and_extract_url,
    extract_playlist_id,
    format_duration,
    is_playlist_url,
    is_pure_playlist_url,
)


class TestPlaylistFunctions(unittest.TestCase):
    def test_clean_and_extract_url(self):
        # Plain clean url
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(clean_and_extract_url(url), url)

        # Quoted url
        self.assertEqual(clean_and_extract_url(f'"{url}"'), url)
        self.assertEqual(clean_and_extract_url(f"'{url}'"), url)

        # Embedded in log string
        log_text = (
            "2026-11-24 13:54:21 INFO Fetching: ['yt-dlp.exe', '--', "
            "'https://www.youtube.com/playlist?list=PLQEaRBV9gAFsR15tNo2QLF9d2qc-c018p']"
        )
        expected = "https://www.youtube.com/playlist?list=PLQEaRBV9gAFsR15tNo2QLF9d2qc-c018p"
        self.assertEqual(clean_and_extract_url(log_text), expected)

        # Empty / whitespace
        self.assertEqual(clean_and_extract_url(""), "")
        self.assertEqual(clean_and_extract_url("   "), "")

    def test_is_playlist_url(self):
        self.assertTrue(
            is_playlist_url("https://www.youtube.com/playlist?list=PL123456")
        )
        self.assertTrue(
            is_playlist_url("https://www.youtube.com/watch?v=abc&list=PL123456")
        )
        self.assertFalse(
            is_playlist_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        )
        self.assertFalse(is_playlist_url(""))

    def test_is_pure_playlist_url(self):
        self.assertTrue(
            is_pure_playlist_url("https://www.youtube.com/playlist?list=PL123456")
        )
        self.assertFalse(
            is_pure_playlist_url(
                "https://www.youtube.com/watch?v=abc&list=PL123456"
            )
        )

    def test_extract_playlist_id(self):
        self.assertEqual(
            extract_playlist_id(
                "https://www.youtube.com/playlist?list=PL123456&si=xyz"
            ),
            "PL123456",
        )
        self.assertEqual(
            extract_playlist_id(
                "https://www.youtube.com/watch?v=abc&list=PL9999"
            ),
            "PL9999",
        )

    def test_format_duration(self):
        self.assertEqual(format_duration(None), "--:--")
        self.assertEqual(format_duration("invalid"), "--:--")
        self.assertEqual(format_duration(0), "0:00")
        self.assertEqual(format_duration(45), "0:45")
        self.assertEqual(format_duration(125), "2:05")
        self.assertEqual(format_duration(3665), "1:01:05")


if __name__ == "__main__":
    unittest.main()
