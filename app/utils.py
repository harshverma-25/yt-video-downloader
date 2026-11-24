import platform
import shutil
from pathlib import Path

import tomlkit
from PySide6 import QtCore
from platformdirs import user_data_dir

ROOT = Path(__file__).parent
BIN_DIR = Path(user_data_dir("yt-video-downloader"))  # user data dir for persistence
LEGACY_BIN_DIR = Path(user_data_dir("yt-dlp-gui"))  # legacy data dir compatibility


def get_ytdlp_path() -> str:
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
