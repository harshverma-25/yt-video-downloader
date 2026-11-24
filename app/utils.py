import os
import platform
import shutil
import sys
from pathlib import Path

import tomlkit
from PySide6 import QtCore
from platformdirs import user_data_dir

ROOT = Path(__file__).parent


def get_app_dir() -> Path:
    """Return root directory of the application executable or source."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_bundle_dir() -> Path:
    """Return directory containing bundled read-only resources."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def is_portable_mode(app_dir: Path | None = None) -> bool:
    """Return True only when an explicit portable marker (portable.txt) exists."""
    target_dir = app_dir if app_dir is not None else get_app_dir()
    try:
        marker = target_dir / "portable.txt"
        return marker.is_file()
    except Exception:
        return False


def get_data_dir(app_dir: Path | None = None) -> Path:
    """Return writable data directory (local appdata or portable data folder)."""
    target_dir = app_dir if app_dir is not None else get_app_dir()
    if is_portable_mode(target_dir):
        data_dir = target_dir / "data"
    else:
        data_dir = Path(user_data_dir("yt-video-downloader", appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to a resource, works for dev and for PyInstaller."""
    # 1. Check sys._MEIPASS (PyInstaller bundle)
    if hasattr(sys, "_MEIPASS"):
        p = Path(sys._MEIPASS) / relative_path
        if p.exists():
            return p
        # Check inside app/ in _MEIPASS
        p_app = Path(sys._MEIPASS) / "app" / relative_path
        if p_app.exists():
            return p_app

    # 2. Check executable directory (onedir dist)
    if getattr(sys, "frozen", False):
        p_exe = Path(sys.executable).resolve().parent / relative_path
        if p_exe.exists():
            return p_exe
        p_app_exe = Path(sys.executable).resolve().parent / "app" / relative_path
        if p_app_exe.exists():
            return p_app_exe

    # 3. Development environment: check ROOT and parent repo
    p_root = ROOT / relative_path
    if p_root.exists():
        return p_root
    p_parent = ROOT.parent / relative_path
    if p_parent.exists():
        return p_parent
    return p_root


def get_config_path(app_dir: Path | None = None) -> Path:
    """Return path to user's writable configuration file."""
    return get_data_dir(app_dir) / "config.toml"


def get_log_path(app_dir: Path | None = None) -> Path:
    """Return path to user's writable debug log file."""
    return get_data_dir(app_dir) / "debug.log"


def get_bin_dir(app_dir: Path | None = None) -> Path:
    """Return primary binary directory for dependencies."""
    bin_dir = get_data_dir(app_dir) / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    return bin_dir


# Data directory and binary directory definitions
DATA_DIR = get_data_dir()
BIN_DIR = get_bin_dir()
LEGACY_BIN_DIR = Path(user_data_dir("yt-dlp-gui"))  # legacy data dir compatibility


def get_bin_dirs(app_dir: Path | None = None) -> list[Path]:
    """Return all directories where binaries might be located."""
    primary_bin = get_bin_dir(app_dir)
    primary_data = get_data_dir(app_dir)
    appdata_dir = Path(user_data_dir("yt-video-downloader", appauthor=False))
    dirs = [
        primary_bin,
        primary_data,
        appdata_dir / "bin",
        appdata_dir,
        LEGACY_BIN_DIR,
        ROOT / "bin",
    ]
    # Filter unique directories
    unique_dirs = []
    for d in dirs:
        if d not in unique_dirs:
            unique_dirs.append(d)
    return unique_dirs


def get_ytdlp_path() -> str:
    """Find the yt-dlp executable across bin directories or system PATH."""
    system_os = platform.system()
    exe_name = "yt-dlp.exe" if system_os == "Windows" else "yt-dlp"
    for d in get_bin_dirs():
        p = d / exe_name
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
    for d in get_bin_dirs():
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
