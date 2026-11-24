import platform
import shutil
from pathlib import Path

import tomlkit
from PySide6 import QtCore
from platformdirs import user_data_dir

ROOT = Path(__file__).parent
BIN_DIR = Path(user_data_dir("yt-video-downloader"))  # user data dir for persistence
LEGACY_BIN_DIR = Path(user_data_dir("yt-dlp-gui"))  # legacy data dir compatibility


def get_bin_dirs() -> list[Path]:
    """Return all directories where binaries might be located."""
    return [BIN_DIR, LEGACY_BIN_DIR, ROOT / "bin"]


def get_ytdlp_path() -> str:
    """Find the yt-dlp executable across bin directories or system PATH."""
    system_os = platform.system()
    exe_name = "yt-dlp.exe" if system_os == "Windows" else "yt-dlp"
    for p in [
        BIN_DIR / exe_name,
        LEGACY_BIN_DIR / exe_name,
        ROOT / "bin" / exe_name,
    ]:
        if p.exists():
            return str(p)
    w = shutil.which("yt-dlp")
    if w:
        return w
    return "yt-dlp"


def get_ffmpeg_dir() -> Path | None:
    """Find directory containing ffmpeg/ffprobe executable."""
    system_os = platform.system()
    exe_name = "ffmpeg.exe" if system_os == "Windows" else "ffmpeg"
    for d in [BIN_DIR, LEGACY_BIN_DIR, ROOT / "bin"]:
        if (d / exe_name).exists():
            return d
    return None


def get_default_download_dir() -> str:
    """Return the user's standard Downloads directory."""
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        return str(downloads)
    return str(Path.home())


def load_toml(path):
    with open(path, "r", encoding="utf-8") as file:
        return tomlkit.parse(file.read())


def save_toml(path, data):
    with open(path, "w", encoding="utf-8") as file:
        file.write(tomlkit.dumps(data))


class ItemRoles:
    IdRole = QtCore.Qt.UserRole
    LinkRole = QtCore.Qt.UserRole + 1
    PathRole = QtCore.Qt.UserRole + 2


QUALITY_OPTIONS = [
    "Best",
    "4320p (8K)",
    "2160p (4K)",
    "1440p (2K)",
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p",
]


class TreeColumn:
    TITLE = 0
    PRESET = 1
    QUALITY = 2
    SIZE = 3
    PROGRESS = 4
    STATUS = 5
    SPEED = 6
    ETA = 7
