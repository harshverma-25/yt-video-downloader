import json
import logging
import os
import re
import subprocess as sp
import sys
from urllib.parse import parse_qs, urlparse

import qtawesome as qta
from PySide6 import QtCore, QtGui, QtWidgets
from utils import BIN_DIR, ROOT, QUALITY_OPTIONS, get_ytdlp_path

logger = logging.getLogger(__name__)


def clean_and_extract_url(raw_text: str) -> str:
    """Extract and clean a valid URL from input text, handling quotes or pasted logs."""
    if not raw_text:
        return ""
    text = raw_text.strip().strip("'\"`")
    # If the user pasted text containing an embedded URL (e.g. from a log or message)
    url_match = re.search(r"https?://[^\s'\"`<>]+", text)
    if url_match:
        return url_match.group(0).rstrip(")]}>.,;'\"")
    return text


def is_playlist_url(url: str) -> bool:
    """Return True if the URL contains playlist indicators."""
    cleaned = clean_and_extract_url(url)
    url_lower = cleaned.lower()
    if not url_lower:
        return False
    if "list=" in url_lower or "/playlist" in url_lower:
        return True
    return False


def is_pure_playlist_url(url: str) -> bool:
    """Return True if URL is strictly a playlist page and not a watch link."""
    url_lower = url.lower().strip()
    return "/playlist" in url_lower and "watch?" not in url_lower


def extract_playlist_id(url: str) -> str:
    """Extract list ID from URL query parameters."""
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        return qs.get("list", [""])[0]
    except Exception:
        return ""


def format_duration(seconds) -> str:
    """Format duration in seconds into HH:MM:SS or MM:SS."""
    if seconds is None:
        return "--:--"
    try:
        s = int(seconds)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
    except (ValueError, TypeError):
        return "--:--"


class PlaylistFetchWorker(QtCore.QThread):
    finished = QtCore.Signal(dict)
    error = QtCore.Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = clean_and_extract_url(url)
        self._is_cancelled = False
        self._process = None

    def cancel(self):
        self._is_cancelled = True
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass
        self.terminate()

    def run(self):
        try:
            create_window = sp.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ytdlp_exe = get_ytdlp_path()
            cmd = [
                ytdlp_exe,
                "--flat-playlist",
                "-J",
                "--no-warnings",
                "--socket-timeout",
                "25",
                "--",
                self.url,
            ]
            logger.info(f"Fetching playlist info: {cmd}")
            env = os.environ.copy()
            env["PATH"] = (
                str(BIN_DIR)
                + os.pathsep
                + str(ROOT / "bin")
                + os.pathsep
                + env.get("PATH", "")
            )
            self._process = sp.Popen(
                cmd,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=create_window,
                env=env,
            )
            stdout, stderr = self._process.communicate()

            if self._is_cancelled:
                return

            if self._process.returncode != 0:
                err_msg = stderr.strip() or "Failed to fetch playlist information"
                logger.error(f"Playlist fetch error: {err_msg}")
                self.error.emit(err_msg)
                return

            data = json.loads(stdout)
            self.finished.emit(data)
        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Playlist fetch exception: {e}", exc_info=True)
                self.error.emit(str(e))


class PlaylistDialog(QtWidgets.QDialog):
    """Modern modal dialog showing all videos in a playlist with selection options."""

    def __init__(
        self,
        parent,
        playlist_data: dict,
        presets: dict,
        default_preset: str = "best",
        default_quality: str = "Best",
    ):
        super().__init__(parent)
        self.playlist_data = playlist_data
        self.presets = presets
        self.raw_entries = playlist_data.get("entries", [])
        self.entries = []
        self._normalize_entries()

        self.setWindowTitle(
            f"Playlist: {self.playlist_data.get('title', 'YouTube Playlist')}"
        )
        self.resize(880, 640)
        self.setMinimumSize(720, 480)

        self._build_ui(default_preset, default_quality)
        self._populate_table()
        self._update_selection_counter()

    def _normalize_entries(self):
        """Filter out unavailable videos and ensure clean title, url, duration."""
        for idx, entry in enumerate(self.raw_entries, 1):
            if not entry:
                continue
            title = entry.get("title") or f"Video #{idx}"
            if title.strip() in ("[Private video]", "[Deleted video]"):
                continue

            video_id = entry.get("id", "")
            url = entry.get("url") or ""
            if url and not url.startswith("http"):
                url = f"https://www.youtube.com/watch?v={url}"
            elif not url and video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"

            if not url:
                continue

            duration = entry.get("duration")
            self.entries.append(
                {
                    "index": idx,
                    "id": video_id,
                    "title": title,
                    "url": url,
                    "duration": duration,
                    "duration_str": format_duration(duration),
                }
            )

    def _build_ui(self, default_preset: str, default_quality: str):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header card
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(14)

        icon_label = QtWidgets.QLabel()
        icon_label.setPixmap(
            qta.icon("mdi6.playlist-play", color="#818cf8").pixmap(46, 46)
        )
        header_layout.addWidget(icon_label)

        title_layout = QtWidgets.QVBoxLayout()
        title_layout.setSpacing(2)

        title_text = self.playlist_data.get("title") or "YouTube Playlist"
        self.lb_title = QtWidgets.QLabel(title_text)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.lb_title.setFont(font)
        self.lb_title.setStyleSheet("color: #f8fafc;")

        uploader = (
            self.playlist_data.get("uploader")
            or self.playlist_data.get("channel")
            or ""
        )
        subtitle = (
            f"By {uploader} • {len(self.entries)} videos available"
            if uploader
            else f"{len(self.entries)} videos available"
        )
        self.lb_subtitle = QtWidgets.QLabel(subtitle)
        self.lb_subtitle.setStyleSheet("color: #94a3b8; font-size: 12px;")

        title_layout.addWidget(self.lb_title)
        title_layout.addWidget(self.lb_subtitle)
        header_layout.addLayout(title_layout, 1)

        # Selection Badge
        self.badge_selection = QtWidgets.QLabel()
        self.badge_selection.setStyleSheet(
            "background-color: #1e2238; color: #818cf8; border: 1px solid #3730a3; "
            "border-radius: 6px; padding: 6px 12px; font-weight: 600; font-size: 12px;"
        )
        header_layout.addWidget(self.badge_selection)

        layout.addLayout(header_layout)

        # Format & Quality Quick Options Bar
        fmt_frame = QtWidgets.QFrame()
        fmt_frame.setStyleSheet(
            "background-color: #161824; border: 1px solid #26293d; border-radius: 8px;"
        )
        fmt_layout = QtWidgets.QHBoxLayout(fmt_frame)
        fmt_layout.setContentsMargins(12, 8, 12, 8)
        fmt_layout.setSpacing(12)

        lb_opt = QtWidgets.QLabel("Format Options:")
        lb_opt.setStyleSheet(
            "font-weight: 600; color: #cbd5e1; border: none; background: transparent;"
        )
        fmt_layout.addWidget(lb_opt)

        lb_p = QtWidgets.QLabel("Preset:")
        lb_p.setStyleSheet("color: #94a3b8; border: none; background: transparent;")
        fmt_layout.addWidget(lb_p)

        self.dd_preset = QtWidgets.QComboBox()
        self.dd_preset.addItems(list(self.presets.keys()))
        if default_preset in self.presets:
            self.dd_preset.setCurrentText(default_preset)
        self.dd_preset.currentTextChanged.connect(self._on_preset_changed)
        fmt_layout.addWidget(self.dd_preset)

        lb_q = QtWidgets.QLabel("Quality:")
        lb_q.setStyleSheet("color: #94a3b8; border: none; background: transparent;")
        fmt_layout.addWidget(lb_q)

        self.dd_quality = QtWidgets.QComboBox()
        self.dd_quality.addItems(QUALITY_OPTIONS)
        if default_quality in QUALITY_OPTIONS:
            self.dd_quality.setCurrentText(default_quality)
        fmt_layout.addWidget(self.dd_quality)

        fmt_layout.addStretch(1)

        layout.addWidget(fmt_frame)

        # Search and Selection Controls Bar
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.setSpacing(10)

        self.le_search = QtWidgets.QLineEdit()
        self.le_search.setPlaceholderText("Filter videos by title...")
        self.le_search.addAction(
            qta.icon("mdi6.magnify", color="#94a3b8"),
            QtWidgets.QLineEdit.ActionPosition.LeadingPosition,
        )
        self.le_search.setClearButtonEnabled(True)
        self.le_search.textChanged.connect(self._filter_table)
        controls_layout.addWidget(self.le_search, 1)

        self.btn_select_all = QtWidgets.QPushButton("Select All")
        self.btn_select_all.setIcon(qta.icon("mdi6.check-all", color="#e2e8f0"))
        self.btn_select_all.clicked.connect(self._select_all)
        controls_layout.addWidget(self.btn_select_all)

        self.btn_deselect_all = QtWidgets.QPushButton("Deselect All")
        self.btn_deselect_all.setIcon(
            qta.icon("mdi6.checkbox-blank-outline", color="#e2e8f0")
        )
        self.btn_deselect_all.clicked.connect(self._deselect_all)
        controls_layout.addWidget(self.btn_deselect_all)

        self.btn_invert = QtWidgets.QPushButton("Invert")
        self.btn_invert.setIcon(qta.icon("mdi6.swap-horizontal", color="#e2e8f0"))
        self.btn_invert.clicked.connect(self._invert_selection)
        controls_layout.addWidget(self.btn_invert)

        layout.addLayout(controls_layout)

        # Videos Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "#", "Title", "Duration"])
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 44)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 52)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 90)

        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table, 1)

        # Bottom Button Bar
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.setMinimumWidth(90)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        btn_layout.addStretch(1)

        self.btn_add_all = QtWidgets.QPushButton(f"Download All ({len(self.entries)})")
        self.btn_add_all.setIcon(qta.icon("mdi6.playlist-check", color="#ffffff"))
        self.btn_add_all.setStyleSheet(
            "background-color: #2e3352; color: #ffffff; border: 1px solid #4338ca; padding: 7px 16px;"
        )
        self.btn_add_all.clicked.connect(self._on_download_all)
        btn_layout.addWidget(self.btn_add_all)

        self.btn_add_selected = QtWidgets.QPushButton("Download Selected (0)")
        self.btn_add_selected.setIcon(qta.icon("mdi6.download", color="#ffffff"))
        self.btn_add_selected.setStyleSheet(
            "background-color: #4f46e5; color: #ffffff; font-weight: 600; border: 1px solid #6366f1; padding: 7px 20px;"
        )
        self.btn_add_selected.clicked.connect(self._on_download_selected)
        btn_layout.addWidget(self.btn_add_selected)

        layout.addLayout(btn_layout)

        # Sync audio / quality state
        self._on_preset_changed(self.dd_preset.currentText())

    def _on_preset_changed(self, preset_name):
        preset_cmd = self.presets.get(preset_name, "")
        preset_args = (
            preset_cmd if isinstance(preset_cmd, list) else preset_cmd.split()
        )
        is_audio = "--extract-audio" in preset_args or "-x" in preset_args
        self.dd_quality.setEnabled(not is_audio)

    def _populate_table(self):
        self.table.setRowCount(len(self.entries))
        for row, entry in enumerate(self.entries):
            # Checkbox item
            chk_item = QtWidgets.QTableWidgetItem()
            chk_item.setFlags(
                QtCore.Qt.ItemFlag.ItemIsUserCheckable
                | QtCore.Qt.ItemFlag.ItemIsEnabled
            )
            chk_item.setCheckState(QtCore.Qt.CheckState.Checked)
            chk_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, chk_item)

            # Index item
            idx_item = QtWidgets.QTableWidgetItem(str(entry["index"]))
            idx_item.setFlags(
                QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable
            )
            idx_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            idx_item.setForeground(QtGui.QColor("#94a3b8"))
            self.table.setItem(row, 1, idx_item)

            # Title item
            title_item = QtWidgets.QTableWidgetItem(entry["title"])
            title_item.setFlags(
                QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable
            )
            title_item.setToolTip(entry["title"])
            self.table.setItem(row, 2, title_item)

            # Duration item
            dur_item = QtWidgets.QTableWidgetItem(entry["duration_str"])
            dur_item.setFlags(
                QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable
            )
            dur_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            dur_item.setForeground(QtGui.QColor("#94a3b8"))
            self.table.setItem(row, 3, dur_item)

        self.table.itemChanged.connect(self._on_item_changed)

    def _on_cell_clicked(self, row, col):
        # Allow toggling checkbox by clicking index or title
        if col != 0:
            item = self.table.item(row, 0)
            if item:
                new_state = (
                    QtCore.Qt.CheckState.Unchecked
                    if item.checkState() == QtCore.Qt.CheckState.Checked
                    else QtCore.Qt.CheckState.Checked
                )
                item.setCheckState(new_state)

    def _on_item_changed(self, item):
        if item.column() == 0:
            self._update_selection_counter()

    def _update_selection_counter(self):
        selected_count = sum(
            1
            for row in range(self.table.rowCount())
            if self.table.item(row, 0)
            and self.table.item(row, 0).checkState() == QtCore.Qt.CheckState.Checked
        )
        total_count = len(self.entries)
        self.badge_selection.setText(
            f"Selected: {selected_count} / {total_count} videos"
        )
        self.btn_add_selected.setText(f"Download Selected ({selected_count})")
        self.btn_add_selected.setEnabled(selected_count > 0)

    def _select_all(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)
                if item:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
        self.table.blockSignals(False)
        self._update_selection_counter()

    def _deselect_all(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)
                if item:
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.table.blockSignals(False)
        self._update_selection_counter()

    def _invert_selection(self):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                item = self.table.item(row, 0)
                if item:
                    new_state = (
                        QtCore.Qt.CheckState.Unchecked
                        if item.checkState() == QtCore.Qt.CheckState.Checked
                        else QtCore.Qt.CheckState.Checked
                    )
                    item.setCheckState(new_state)
        self.table.blockSignals(False)
        self._update_selection_counter()

    def _filter_table(self, text: str):
        query = text.strip().lower()
        for row in range(self.table.rowCount()):
            title_item = self.table.item(row, 2)
            title = title_item.text().lower() if title_item else ""
            match = query in title if query else True
            self.table.setRowHidden(row, not match)

    def _on_download_all(self):
        self._select_all()
        self.accept()

    def _on_download_selected(self):
        self.accept()

    def get_selected_videos(self):
        """Return list of entry dicts for all checked rows."""
        selected = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == QtCore.Qt.CheckState.Checked:
                selected.append(self.entries[row])
        return selected

    def get_preset(self) -> str:
        return self.dd_preset.currentText()

    def get_quality(self) -> str:
        preset = self.get_preset()
        preset_cmd = self.presets.get(preset, "")
        preset_args = (
            preset_cmd if isinstance(preset_cmd, list) else preset_cmd.split()
        )
        is_audio = "--extract-audio" in preset_args or "-x" in preset_args
        return "N/A" if is_audio else self.dd_quality.currentText()

