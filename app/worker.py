import logging
import os
import shlex
import subprocess as sp
import sys

from PySide6 import QtCore, QtWidgets
from utils import BIN_DIR, ROOT, ItemRoles, TreeColumn, get_ytdlp_path

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
        p_args = config["presets"][self.preset]
        g_args = config["general"].get("global_args")

        args += ["-P", self.path]
        p_args_list = p_args if isinstance(p_args, list) else shlex.split(p_args)
        args += p_args_list

        if self.quality and self.quality not in ("Best", "N/A", "-"):
            is_audio = "--extract-audio" in p_args_list or "-x" in p_args_list
            if not is_audio:
                height = self.quality.split("p")[0].strip()
                args += ["-S", f"res:{height}"]

        args += g_args if isinstance(g_args, list) else shlex.split(g_args)
        args += ["--", self.link]
        return args

    def stop(self):
        with QtCore.QMutexLocker(self._mutex):
            self._stop = True

    def run(self):
        create_window = sp.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        output = ""
        logger.info(f"Download ({self.id}) starting with cmd: {self.command}")

        env = os.environ.copy()
        env["PATH"] = str(BIN_DIR) + os.pathsep + str(ROOT / "bin") + os.pathsep + env.get("PATH", "")

        self.progress.emit(self.item, [(TreeColumn.STATUS, "Processing")])

        with sp.Popen(
            self.command,
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            text=True,
            universal_newlines=True,
            creationflags=create_window,
            env=env,
        ) as p:
            for line in p.stdout:
                output += line
                with QtCore.QMutexLocker(self._mutex):
                    if self._stop:
                        p.terminate()
                        p.wait()
                        logger.info(f"Download ({self.id}) stopped.")
                        break

                line = line.strip()
                if "__SEP__" in line:
                    status, total_bytes, percent, speed, eta, title = [
                        i.strip() for i in line.split("__SEP__")
                    ]
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
                elif line.startswith(("[Merger]", "[ExtractAudio]")):
                    self.progress.emit(self.item, [(TreeColumn.STATUS, "Converting")])
                elif line.startswith("WARNING:"):
                    logger.warning(f"Download ({self.id}) {line}")

        if p.returncode != 0:
            logger.error(f"Download ({self.id}) returncode: {p.returncode}\n{output}")
            self.progress.emit(self.item, [(TreeColumn.STATUS, "ERROR")])
        else:
            logger.info(f"Download ({self.id}) finished.")
            self.progress.emit(
                self.item,
                [
                    (TreeColumn.PROGRESS, "100%"),
                    (TreeColumn.STATUS, "Finished"),
                ],
            )
