"""
Automatic Dependency Downloader and Updater for YT Video Downloader.
Handles secure download, checksum validation, safe ZIP extraction, and updates
for external backend binaries (yt-dlp, FFmpeg, FFprobe, Deno).
"""

import hashlib
import logging
import os
import platform
import shutil
import stat
import subprocess as sp
import sys
import zipfile
from pathlib import Path
from typing import List, Tuple

import requests
from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

from utils import (
    ROOT,
    BIN_DIR,
    LEGACY_BIN_DIR,
    get_bin_dir,
    get_bin_dirs,
    get_ytdlp_path,
    is_appdata_path,
    is_portable_mode,
)

logger = logging.getLogger(__name__)

# Mutex to ensure only one dependency worker runs at a time
_DEP_MUTEX = QMutex()
_IS_DEP_WORKER_RUNNING = False

BINARIES = {
    "Linux": {
        "ffmpeg": "ffmpeg-linux64-v4.1",
        "ffprobe": "ffprobe-linux64-v4.1",
        "yt-dlp": "yt-dlp_linux",
        "deno": "deno-x86_64-unknown-linux-gnu.zip",
    },
    "Darwin": {
        "ffmpeg": "ffmpeg-osx64-v4.1",
        "ffprobe": "ffprobe-osx64-v4.1",
        "yt-dlp": "yt-dlp_macos",
        "deno": "deno-x86_64-apple-darwin.zip",
    },
    "Windows": {
        "ffmpeg": "ffmpeg-win64-v4.1.exe",
        "ffprobe": "ffprobe-win64-v4.1.exe",
        "yt-dlp": "yt-dlp.exe",
        "deno": "deno-x86_64-pc-windows-msvc.zip",
    },
}

YT_DLP_BASE_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/"
FFMPEG_BASE_URL = "https://github.com/imageio/imageio-binaries/raw/183aef992339cc5a463528c75dd298db15fd346f/ffmpeg/"
DENO_BASE_URL = "https://github.com/denoland/deno/releases/latest/download/"

# Official SHA-256 hashes for immutable pinned dependencies (imageio-binaries commit 183aef9).
# Note: Floating latest releases (yt-dlp, deno) change continuously upstream and cannot be pinned to
# fixed static hashes; their integrity is verified via HTTPS transport, size checks, and ZIP testing.
PINNED_CHECKSUMS = {
    "ffmpeg-win64-v4.1.exe": "62b2b2c72d7b8cb23a57c750a1a4380c0e6104dd4a2f121bd5bf21281287f88f",
    "ffprobe-win64-v4.1.exe": "6ed1b84b3ad0c93d20350ace17661f1e862e26fdb4f9a5a3457d40e4da6355da",
}


def compute_sha256(file_path: Path | str) -> str:
    """Compute sha256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


class DepWorker(QThread):
    progress = Signal(str)

    def __init__(self, update_ytdlp: bool, active_downloads_callback=None):
        super().__init__()
        self.missing: List[Tuple[str, str, str]] = []  # (exe_name, download_url, target_path)
        self.update_ytdlp = update_ytdlp
        self.active_downloads_callback = active_downloads_callback

    def _check_missing_dependencies(self):
        system_os = platform.system()
        if system_os not in BINARIES:
            logger.warning(f"Unsupported operating system for auto-dependencies: {system_os}")
            return

        required_binaries = ["ffmpeg", "ffprobe", "yt-dlp", "deno"]
        bin_dir = get_bin_dir()
        bin_dirs = get_bin_dirs()
        portable = is_portable_mode()
        missing_exes = []

        for exe in required_binaries:
            exe_ext = f"{exe}.exe" if system_os == "Windows" else exe

            # 1. Check all allowed mode-specific directories
            found = False
            for d in bin_dirs:
                if (d / exe_ext).exists():
                    found = True
                    break
            if found:
                continue

            # 2. Seamless migration if present in legacy data dir (installed mode only)
            if not portable and (LEGACY_BIN_DIR / exe_ext).exists():
                try:
                    bin_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(LEGACY_BIN_DIR / exe_ext, bin_dir / exe_ext)
                    logger.info(f"Migrated legacy binary {exe} to {bin_dir}")
                    continue
                except Exception as e:
                    logger.warning(f"Could not copy legacy binary {exe}: {e}")

            # 3. Source development fallback (installed/dev mode only)
            if not portable and (ROOT / "bin" / exe_ext).exists():
                continue

            # 4. System PATH check (strictly prevent portable mode from using AppData binaries)
            which_path = shutil.which(exe)
            if which_path:
                if portable and is_appdata_path(which_path):
                    logger.debug(f"Ignoring AppData binary in portable mode: {which_path}")
                else:
                    continue

            missing_exes.append(exe)

        if not missing_exes:
            return

        bin_dir.mkdir(parents=True, exist_ok=True)

        for exe in missing_exes:
            binary_name = BINARIES[system_os][exe]

            if exe == "yt-dlp":
                url = YT_DLP_BASE_URL + binary_name
            elif exe == "deno":
                url = DENO_BASE_URL + binary_name
            else:
                url = FFMPEG_BASE_URL + binary_name

            target_name = f"{exe}.exe" if system_os == "Windows" else exe
            target_path = str(bin_dir / target_name)

            self.missing.append((exe, url, target_path))

    def _set_executable_permissions(self, file_path: str):
        """Set executable permissions on Linux and macOS."""
        if platform.system() != "Windows":
            try:
                st = os.stat(file_path)
                os.chmod(file_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            except OSError as e:
                logger.warning(f"Failed to set executable permissions on {file_path}: {e}")

    def run(self):
        global _IS_DEP_WORKER_RUNNING
        with QMutexLocker(_DEP_MUTEX):
            if _IS_DEP_WORKER_RUNNING:
                logger.warning("Another DepWorker instance is already running; skipping.")
                return
            _IS_DEP_WORKER_RUNNING = True

        try:
            self._check_missing_dependencies()

            if self.missing:
                for exe, url, target_path in self.missing:
                    success = self._download_dependency(exe, url, target_path)
                    if success:
                        self._set_executable_permissions(target_path)
                    else:
                        logger.error(f"Failed downloading required dependency '{exe}' from {url}")

            if self.update_ytdlp:
                self.update()
        except Exception as e:
            logger.error(f"Error during dependency check/update: {e}", exc_info=True)
            self.progress.emit("Warning: Dependency check encountered an error.")
        finally:
            with QMutexLocker(_DEP_MUTEX):
                _IS_DEP_WORKER_RUNNING = False
            self.finished.emit()

    def update(self):
        """Check for and apply yt-dlp self-update safely."""
        # Avoid running update during active downloads
        if self.active_downloads_callback and self.active_downloads_callback():
            logger.info("Active downloads in progress; deferring yt-dlp update check.")
            return

        ytdlp_exe = get_ytdlp_path()
        if not Path(ytdlp_exe).exists() and not shutil.which(ytdlp_exe):
            logger.warning("Cannot update yt-dlp: executable not found.")
            return

        create_window = sp.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        output = ""
        updated = False

        env = os.environ.copy()
        bin_paths = [str(d) for d in get_bin_dirs()]
        env["PATH"] = os.pathsep.join(bin_paths) + os.pathsep + env.get("PATH", "")

        try:
            self.progress.emit("Checking for yt-dlp updates...")
            with sp.Popen(
                [ytdlp_exe, "-U"],
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=create_window,
                env=env,
            ) as p:
                for line in p.stdout:
                    output += line
                    if "Updating to" in line or "Updated yt-dlp" in line:
                        updated = True
                        self.progress.emit("Updating yt-dlp...")

            if p.returncode != 0:
                logger.warning(f"yt-dlp update returned code {p.returncode}: {output.strip()}")
            elif updated:
                self.progress.emit("yt-dlp updated successfully.")
                logger.info(f"yt-dlp updated successfully:\n{output.strip()}")
        except Exception as e:
            logger.warning(f"Unable to execute yt-dlp update: {e}")

    def _download_dependency(self, exe: str, url: str, target_path: str) -> bool:
        """Securely download and install a binary or ZIP package."""
        display_name = os.path.basename(target_path)
        temp_part = target_path + ".part"
        is_zip = url.endswith(".zip")
        temp_zip = target_path + ".part.zip" if is_zip else None
        download_target = temp_zip if is_zip else temp_part

        # Clean up any stale partial files before starting
        for p in (temp_part, temp_zip):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

        try:
            # 1. Perform HTTP request with explicit timeout and context manager
            with requests.get(url, stream=True, timeout=(10, 30)) as response:
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                block_size = 16384
                downloaded = 0
                hasher = hashlib.sha256()

                with open(download_target, "wb") as f:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        hasher.update(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            percentage = int((downloaded / total_size) * 100)
                            dl_mb = downloaded / (1024 * 1024)
                            tot_mb = total_size / (1024 * 1024)
                            status = f"Downloading {display_name}: {dl_mb:.2f}/{tot_mb:.2f} MB ({percentage}%)"
                        else:
                            dl_mb = downloaded / (1024 * 1024)
                            status = f"Downloading {display_name}: {dl_mb:.2f} MB"
                        self.progress.emit(status)

            # 2. Basic download integrity verification
            if downloaded == 0:
                raise ValueError(f"Downloaded empty payload for {display_name}")

            if total_size > 0 and downloaded != total_size:
                raise ValueError(
                    f"Incomplete download for {display_name}: expected {total_size} bytes, got {downloaded}"
                )

            # Verify pinned checksum if available
            raw_binary_name = os.path.basename(url)
            if raw_binary_name in PINNED_CHECKSUMS:
                expected_sha = PINNED_CHECKSUMS[raw_binary_name]
                actual_sha = hasher.hexdigest().lower()
                if actual_sha != expected_sha:
                    raise ValueError(
                        f"Checksum verification failed for {display_name}! Expected {expected_sha}, got {actual_sha}"
                    )
                logger.info(f"Verified SHA-256 for {display_name}: {actual_sha}")

            # 3. Handle ZIP archives (e.g. Deno)
            if is_zip:
                self._extract_zip_executable(temp_zip, temp_part, exe)

            # 4. Atomically install target executable
            os.replace(temp_part, target_path)
            logger.info(f"Successfully installed dependency: {target_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download dependency {display_name} from {url}: {e}")
            self.progress.emit(f"Failed to download {display_name}: {e}")
            return False
        finally:
            # Clean up all temporary files on failure
            for p in (temp_part, temp_zip):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass

    def _extract_zip_executable(self, zip_path: str, extract_dest: str, exe_name: str):
        """Safely extract the specific executable from a zip archive with Zip-Slip protection."""
        if not zipfile.is_zipfile(zip_path):
            raise ValueError(f"Downloaded file {zip_path} is not a valid ZIP archive")

        system_os = platform.system()
        expected_exe = f"{exe_name}.exe" if system_os == "Windows" else exe_name

        with zipfile.ZipFile(zip_path, "r") as zf:
            # Test ZIP integrity
            corrupt = zf.testzip()
            if corrupt:
                raise ValueError(f"Corrupt ZIP file detected at member: {corrupt}")

            target_member = None
            for member in zf.infolist():
                if member.is_dir():
                    continue

                # Zip Slip protection: ensure member filename does not escape
                norm_name = os.path.normpath(member.filename)
                if norm_name.startswith("..") or os.path.isabs(norm_name):
                    raise ValueError(f"Zip Slip path traversal attempt detected: {member.filename}")

                base_name = os.path.basename(member.filename)
                if base_name.lower() == expected_exe.lower():
                    target_member = member
                    break

            if not target_member:
                available = [m.filename for m in zf.infolist()]
                raise ValueError(
                    f"Expected executable '{expected_exe}' not found in archive. Available: {available}"
                )

            # Extract member to temporary destination
            with zf.open(target_member) as source, open(extract_dest, "wb") as target:
                shutil.copyfileobj(source, target)
