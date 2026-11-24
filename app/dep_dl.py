import os
import platform
import shutil
import stat
import sys
import zipfile
from typing import List, Tuple
import logging


import requests
from PySide6.QtCore import QThread, Signal

from utils import ROOT, BIN_DIR, LEGACY_BIN_DIR, get_ytdlp_path, get_bin_dirs
import subprocess as sp

logger = logging.getLogger(__name__)

for d in get_bin_dirs():
    os.environ["PATH"] += os.pathsep + str(d)

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


class DepWorker(QThread):
    progress = Signal(str)

    def __init__(self, update_ytdlp: bool):
        super().__init__()
        self.missing: List[Tuple[str, str]] = []
        self.update_ytdlp = update_ytdlp

    def _check_missing_dependencies(self):
        system_os = platform.system()
        if system_os not in BINARIES:
            return

        required_binaries = ["ffmpeg", "ffprobe", "yt-dlp", "deno"]
        missing_exes = []
        for exe in required_binaries:
            exe_ext = f"{exe}.exe" if system_os == "Windows" else exe
            if (BIN_DIR / exe_ext).exists():
                continue
            # Seamless migration if present in legacy data dir
            if (LEGACY_BIN_DIR / exe_ext).exists():
                try:
                    BIN_DIR.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(LEGACY_BIN_DIR / exe_ext, BIN_DIR / exe_ext)
                    logger.info(f"Migrated legacy binary {exe} to {BIN_DIR}")
                    continue
                except Exception as e:
                    logger.warning(f"Could not copy legacy binary {exe}: {e}")
            if (ROOT / "bin" / exe_ext).exists():
                continue
            if shutil.which(exe):
                continue
            missing_exes.append(exe)

        if not missing_exes:
            return

        BIN_DIR.mkdir(parents=True, exist_ok=True)

        for exe in missing_exes:
            binary_name = BINARIES[system_os][exe]

            if exe == "yt-dlp":
                url = YT_DLP_BASE_URL + binary_name
            elif exe == "deno":
                url = DENO_BASE_URL + binary_name
            else:
                url = FFMPEG_BASE_URL + binary_name

            target_name = f"{exe}.exe" if system_os == "Windows" else exe
            target_path = str(BIN_DIR / target_name)

            self.missing.append((url, target_path))

    def chmod(self):
        try:
            st = os.stat(self.filename)
            os.chmod(self.filename, st.st_mode | stat.S_IEXEC)
        except OSError:
            pass

    def run(self):
        try:
            self._check_missing_dependencies()

            if self.missing:
                for missingexe in self.missing:
                    self.url, self.filename = missingexe
                    success = self._download()
                    if success:
                        self.chmod()

            if self.update_ytdlp:
                self.update()
        except Exception as e:
            logger.error(f"Error checking/updating dependencies: {e}", exc_info=True)
            self.progress.emit("Warning: Dependency check failed or offline mode.")
        finally:
            self.finished.emit()

    def update(self):
        create_window = sp.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        output = ""
        updated = False
        ytdlp_exe = get_ytdlp_path()

        try:
            with sp.Popen(
                [ytdlp_exe, "-U"],
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=create_window,
            ) as p:
                for line in p.stdout:
                    output += line
                    if line.startswith("Updating to"):
                        updated = True
                        self.progress.emit("Updating yt-dlp...")

            if p.returncode != 0:
                logger.warning(f"yt-dlp update returncode {p.returncode}: {output}")
            elif updated:
                self.progress.emit("yt-dlp updated")
                logger.info(f"yt-dlp updated\n{output}")
        except Exception as e:
            logger.warning(f"Unable to run yt-dlp update check: {e}")

    def _download(self) -> bool:
        try:
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to download dependency {self.url}: {e}")
            self.progress.emit(f"Failed to download dependency: {e}")
            return False

        total_size = int(response.headers.get("content-length", 0))
        block_size = 8192
        downloaded = 0

        display_name = os.path.basename(self.filename)
        temp_filename = self.filename + ".part"

        with open(temp_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)

                if total_size > 0:
                    percentage = int((downloaded / total_size) * 100)
                    dl_mb = downloaded / (1024 * 1024)
                    tot_mb = total_size / (1024 * 1024)
                    status = f"Downloading dependency: ({display_name}) {dl_mb:.2f} / {tot_mb:.2f} MB {percentage}%"
                else:
                    percentage = 0
                    dl_mb = downloaded / (1024 * 1024)
                    status = f"{display_name}: {dl_mb:.2f} MB"

                self.progress.emit(status)

        if self.url.endswith(".zip"):
            try:
                zip_filename = temp_filename + ".zip"
                shutil.move(temp_filename, zip_filename)

                with zipfile.ZipFile(zip_filename, "r") as zf:
                    target_filename = zf.namelist()[0]
                    with zf.open(target_filename) as source, open(
                        self.filename, "wb"
                    ) as target:
                        shutil.copyfileobj(source, target)

                if os.path.exists(zip_filename):
                    os.remove(zip_filename)
                return True
            except Exception as e:
                if os.path.exists(zip_filename):
                    os.remove(zip_filename)
                raise e

        if os.path.exists(self.filename):
            os.remove(self.filename)
        os.rename(temp_filename, self.filename)
        return True
