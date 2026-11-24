import logging
import os
import shlex
import shutil
import subprocess as sp
import sys
from pathlib import Path

from PySide6 import QtCore, QtWidgets
from utils import (
    BIN_DIR,
    LEGACY_BIN_DIR,
    ROOT,
    ItemRoles,
    TreeColumn,
    get_bin_dirs,
    get_ffmpeg_dir,
    get_ytdlp_path,
)

logger = logging.getLogger(__name__)


class DownloadWorker(QtCore.QThread):
    progress = QtCore.Signal(object, list)

    def __init__(self, item, config, link, path, preset, quality="Best"):
        super().__init__()
        self.item: QtWidgets.QTreeWidgetItem = item
        self.link = link
        self.path = path
        self.preset = preset
        self.quality = quality
        self.id = self.item.data(0, ItemRoles.IdRole)
        self.command = self.build_command(config)
        self._mutex = QtCore.QMutex()
        self._stop = False
        self.proc: sp.Popen | None = None

    def build_command(self, config):
        ytdlp_exe = get_ytdlp_path()
        args = [
            ytdlp_exe,
            "--newline",
            "--no-simulate",
            "--progress",
            "--progress-template",
            "%(progress.status)s__SEP__%(progress._total_bytes_estimate_str)s__SEP__%(progress._percent_str)s__SEP__%(progress._speed_str)s__SEP__%(progress._eta_str)s__SEP__%(info.title)s",
            # Speed optimization flags for maximum download rate
            "-N",
            "8",
            "--buffer-size",
            "1024k",
            "--http-chunk-size",
            "10M",
            "--no-mtime",
        ]

        # Add FFmpeg location if available in local directories
        ffmpeg_dir = get_ffmpeg_dir()
        if ffmpeg_dir:
            args += ["--ffmpeg-location", str(ffmpeg_dir)]

        p_args = config["presets"].get(self.preset, "")
        g_args = config["general"].get("global_args", "") or ""

        args += ["-P", self.path]

        if isinstance(p_args, list):
            p_args_list = p_args
        elif isinstance(p_args, str) and p_args.strip():
            try:
                p_args_list = shlex.split(p_args)
            except ValueError:
                p_args_list = p_args.split()
        else:
            p_args_list = []
        args += p_args_list

        if self.quality and self.quality not in ("Best", "N/A", "-"):
            is_audio = "--extract-audio" in p_args_list or "-x" in p_args_list
            if not is_audio:
                height = self.quality.split("p")[0].strip()
                args += ["-S", f"res:{height}"]

        if isinstance(g_args, list):
            args += g_args
        elif isinstance(g_args, str) and g_args.strip():
            try:
                args += shlex.split(g_args)
            except ValueError:
                args += g_args.split()

        args += ["--", self.link]
        return args

    def stop(self):
        """Signal worker and child process to stop."""
        with QtCore.QMutexLocker(self._mutex):
            self._stop = True
            proc = self.proc
        if proc is not None:
            try:
                proc.terminate()
            except OSError:
                pass

    def run(self):
        create_window = sp.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        output = ""
        logger.info(f"Download ({self.id}) starting with cmd: {self.command}")

        # Ensure destination directory exists and is writable
        try:
            Path(self.path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Could not create download folder '{self.path}': {e}")
            self.progress.emit(
                self.item,
                [
                    (TreeColumn.STATUS, "ERROR"),
                    (TreeColumn.TITLE, f"Error: Cannot access folder {self.path}"),
                ],
            )
            return

        # Verify yt-dlp executable exists
        ytdlp_exe = self.command[0] if self.command else "yt-dlp"
        if not Path(ytdlp_exe).exists() and not shutil.which(ytdlp_exe):
            logger.error(f"Download ({self.id}) failed: yt-dlp binary '{ytdlp_exe}' not found.")
            self.progress.emit(
                self.item,
                [
                    (TreeColumn.STATUS, "ERROR"),
                    (TreeColumn.TITLE, "Error: yt-dlp executable not found"),
                ],
            )
            return

        env = os.environ.copy()
        bin_paths = [str(d) for d in get_bin_dirs()]
        env["PATH"] = os.pathsep.join(bin_paths) + os.pathsep + env.get("PATH", "")

        self.progress.emit(self.item, [(TreeColumn.STATUS, "Processing")])

        proc_started = False
        returncode = -1

        try:
            with sp.Popen(
                self.command,
                stdout=sp.PIPE,
                stderr=sp.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=create_window,
                env=env,
            ) as p:
                with QtCore.QMutexLocker(self._mutex):
                    self.proc = p
                    proc_started = True

                for line in p.stdout:
                    output += line
                    with QtCore.QMutexLocker(self._mutex):
                        should_stop = self._stop
                    if should_stop:
                        try:
                            p.terminate()
                            p.wait(timeout=2)
                        except (sp.TimeoutExpired, OSError):
                            try:
                                p.kill()
                            except OSError:
                                pass
                        logger.info(f"Download ({self.id}) stopped by user.")
                        break

                    line = line.strip()
                    if "__SEP__" in line:
                        parts = [i.strip() for i in line.split("__SEP__")]
                        if len(parts) >= 6:
                            status = parts[0]
                            total_bytes = parts[1]
                            percent = parts[2]
                            speed = parts[3]
                            eta = parts[4]
                            title = "__SEP__".join(parts[5:])
                            self.progress.emit(
                                self.item,
                                [
                                    (TreeColumn.TITLE, title),
                                    (TreeColumn.SIZE, total_bytes),
                                    (TreeColumn.PROGRESS, percent),
                                    (TreeColumn.SPEED, speed),
                                    (TreeColumn.ETA, eta),
                                    (TreeColumn.STATUS, "Downloading"),
                                ],
                            )
                    elif line.startswith(("[Merger]", "[ExtractAudio]", "[VideoConvertor]")):
                        self.progress.emit(self.item, [(TreeColumn.STATUS, "Converting")])
                    elif line.startswith("WARNING:"):
                        logger.warning(f"Download ({self.id}) {line}")

                returncode = p.wait() if p.returncode is None else p.returncode

        except (OSError, FileNotFoundError, Exception) as e:
            logger.error(f"Download ({self.id}) failed during execution: {e}", exc_info=True)
            self.progress.emit(
                self.item,
                [
                    (TreeColumn.STATUS, "ERROR"),
                    (TreeColumn.SPEED, "-"),
                    (TreeColumn.ETA, "-"),
                ],
            )
            return
        finally:
            with QtCore.QMutexLocker(self._mutex):
                self.proc = None

        with QtCore.QMutexLocker(self._mutex):
            was_stopped = self._stop

        if was_stopped:
            logger.info(f"Download ({self.id}) cancelled.")
            self.progress.emit(
                self.item,
                [
                    (TreeColumn.STATUS, "Cancelled"),
                    (TreeColumn.SPEED, "-"),
                    (TreeColumn.ETA, "-"),
                ],
            )
        elif returncode != 0:
            logger.error(f"Download ({self.id}) returncode: {returncode}\n{output}")
            self.progress.emit(
                self.item,
                [
                    (TreeColumn.STATUS, "ERROR"),
                    (TreeColumn.SPEED, "-"),
                    (TreeColumn.ETA, "-"),
                ],
            )
        else:
            logger.info(f"Download ({self.id}) finished.")
            self.progress.emit(
                self.item,
                [
                    (TreeColumn.PROGRESS, "100%"),
                    (TreeColumn.STATUS, "Finished"),
                    (TreeColumn.SPEED, "-"),
                    (TreeColumn.ETA, "-"),
                ],
            )
