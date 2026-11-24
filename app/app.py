import logging
import sys
from pathlib import Path

import qtawesome as qta
from dep_dl import DepWorker
from playlist_dialog import (
    PlaylistDialog,
    PlaylistFetchWorker,
    clean_and_extract_url,
    is_playlist_url,
)
from PySide6 import QtCore, QtGui, QtWidgets
from style import MODERN_STYLE
from ui.main_window import Ui_MainWindow
from utils import (
    BIN_DIR,
    ROOT,
    ItemRoles,
    TreeColumn,
    QUALITY_OPTIONS,
    get_config_path,
    get_default_download_dir,
    get_log_path,
    get_resource_path,
    load_toml,
    save_toml,
)
from worker import DownloadWorker

__version__ = "v1.0.0"

LOG_PATH = get_log_path()
LOG_DIR = LOG_PATH.parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s (%(module)s:%(lineno)d) %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8", delay=True),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setStyleSheet(MODERN_STYLE)
        icon_path = get_resource_path("assets/yt-video-downloader.ico")
        if not icon_path.exists():
            icon_path = get_resource_path("assets/yt-dlp-gui.ico")
        if icon_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.resize(920, 680)
        self.setMinimumSize(800, 560)

        # Build clean, modern, attractive UI layout
        self._build_modern_ui()

        self.tw.setAlternatingRowColors(True)
        self.tw.setAnimated(True)
        self.tw.setColumnWidth(TreeColumn.TITLE, 280)
        self.tw.setColumnWidth(TreeColumn.PRESET, 80)
        self.tw.setColumnWidth(TreeColumn.QUALITY, 85)
        self.tw.setColumnWidth(TreeColumn.SIZE, 85)
        self.tw.setColumnWidth(TreeColumn.PROGRESS, 120)
        self.tw.setColumnWidth(TreeColumn.STATUS, 95)
        self.tw.setColumnWidth(TreeColumn.SPEED, 85)
        self.tw.setColumnWidth(TreeColumn.ETA, 75)

        self.te_link.setFocus()
        self.load_config()

        self.connect_ui()
        self.pb_download.setEnabled(False)
        self.show()

        self.dep_worker = DepWorker(self.config["general"]["update_ytdlp"])
        self.dep_worker.finished.connect(self.on_dep_finished)
        self.dep_worker.progress.connect(self.on_dep_progress)
        self.dep_worker.start()

        self.to_dl = {}
        self.pending_queue = []
        self.active_workers = {}
        self.MAX_CONCURRENT_DOWNLOADS = 3
        self.index = 0

        self.tw.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tw.customContextMenuRequested.connect(self.open_menu)

    def _build_modern_ui(self):
        """Construct a clean, unified, and modern interface layout."""
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        root_layout = QtWidgets.QVBoxLayout(central)
        root_layout.setContentsMargins(18, 14, 18, 14)
        root_layout.setSpacing(12)

        # 1. Header Bar: Icon + App Title + Status Capsules
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QtWidgets.QLabel()
        icon_pixmap = QtGui.QIcon(str(ROOT / "assets" / "yt-video-downloader.ico")).pixmap(36, 36)
        if icon_pixmap.isNull():
            icon_pixmap = qta.icon("mdi6.play-circle", color="#818cf8").pixmap(36, 36)
        icon_label.setPixmap(icon_pixmap)
        header_layout.addWidget(icon_label)

        title_col = QtWidgets.QVBoxLayout()
        title_col.setSpacing(1)
        lb_app_title = QtWidgets.QLabel("YT Video Downloader")
        font_title = QtGui.QFont()
        font_title.setPointSize(14)
        font_title.setBold(True)
        lb_app_title.setFont(font_title)
        lb_app_title.setStyleSheet("color: #f8fafc;")

        lb_app_sub = QtWidgets.QLabel("Fast, high-quality video and audio downloader")
        lb_app_sub.setStyleSheet("color: #94a3b8; font-size: 11px;")
        title_col.addWidget(lb_app_title)
        title_col.addWidget(lb_app_sub)
        header_layout.addLayout(title_col, 1)

        self.badge_status = QtWidgets.QLabel("🟢 Ready")
        self.badge_status.setStyleSheet(
            "background-color: #141824; border: 1px solid #242b3d; border-radius: 12px; "
            "padding: 5px 14px; color: #34d399; font-weight: 600; font-size: 11px;"
        )
        header_layout.addWidget(self.badge_status)

        self.badge_queue_count = QtWidgets.QLabel("0 Items")
        self.badge_queue_count.setStyleSheet(
            "background-color: #141824; border: 1px solid #242b3d; border-radius: 12px; "
            "padding: 5px 14px; color: #94a3b8; font-weight: 600; font-size: 11px;"
        )
        header_layout.addWidget(self.badge_queue_count)
        root_layout.addLayout(header_layout)

        # 2. Input Card (Mode Tabs + URL Input + Options Strip)
        card_input = QtWidgets.QFrame()
        card_input.setObjectName("card_input")
        card_input_layout = QtWidgets.QVBoxLayout(card_input)
        card_input_layout.setContentsMargins(14, 12, 14, 12)
        card_input_layout.setSpacing(10)

        # Tab Widget for Mode selection
        self.tab_widget = QtWidgets.QTabWidget()

        # Tab 1: Single Video(s)
        tab_videos = QtWidgets.QWidget()
        tab_v_layout = QtWidgets.QVBoxLayout(tab_videos)
        tab_v_layout.setContentsMargins(0, 8, 0, 0)
        tab_v_layout.setSpacing(6)

        tab_v_top = QtWidgets.QHBoxLayout()
        lb_paste_hint = QtWidgets.QLabel("Paste YouTube video link(s):")
        lb_paste_hint.setStyleSheet("color: #94a3b8; font-weight: 500; font-size: 12px;")
        tab_v_top.addWidget(lb_paste_hint)
        tab_v_top.addStretch(1)

        self.pb_paste = QtWidgets.QPushButton(" Paste")
        self.pb_paste.setProperty("class", "btn-subtle")
        self.pb_paste.setIcon(qta.icon("mdi6.content-paste", color="#94a3b8"))
        self.pb_paste.setToolTip("Paste URL from clipboard")
        self.pb_paste.clicked.connect(self.button_paste)
        tab_v_top.addWidget(self.pb_paste)

        self.pb_clear_url = QtWidgets.QPushButton(" Clear")
        self.pb_clear_url.setProperty("class", "btn-subtle")
        self.pb_clear_url.setIcon(qta.icon("mdi6.close-circle-outline", color="#94a3b8"))
        self.pb_clear_url.setToolTip("Clear input box")
        self.pb_clear_url.clicked.connect(self.te_link.clear)
        tab_v_top.addWidget(self.pb_clear_url)
        tab_v_layout.addLayout(tab_v_top)

        self.te_link.setPlaceholderText(
            "Paste one or more video links here (one per line)...\n"
            "Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        self.te_link.setMinimumHeight(65)
        self.te_link.setMaximumHeight(85)
        tab_v_layout.addWidget(self.te_link)

        # Tab 2: YouTube Playlist
        tab_playlist = QtWidgets.QWidget()
        tab_pl_layout = QtWidgets.QVBoxLayout(tab_playlist)
        tab_pl_layout.setContentsMargins(0, 8, 0, 0)
        tab_pl_layout.setSpacing(8)

        pl_input_layout = QtWidgets.QHBoxLayout()
        pl_input_layout.setSpacing(8)

        self.le_playlist = QtWidgets.QLineEdit()
        self.le_playlist.setPlaceholderText(
            "Paste YouTube playlist URL (e.g. https://www.youtube.com/playlist?list=...)"
        )
        self.le_playlist.returnPressed.connect(self.button_fetch_playlist)
        pl_input_layout.addWidget(self.le_playlist, 1)

        self.pb_paste_pl = QtWidgets.QPushButton(" Paste")
        self.pb_paste_pl.setProperty("class", "btn-subtle")
        self.pb_paste_pl.setIcon(qta.icon("mdi6.content-paste", color="#94a3b8"))
        self.pb_paste_pl.clicked.connect(self.button_paste_playlist)
        pl_input_layout.addWidget(self.pb_paste_pl)

        self.pb_fetch_pl = QtWidgets.QPushButton(" Fetch Playlist Videos")
        self.pb_fetch_pl.setIcon(qta.icon("mdi6.playlist-check", color="#ffffff"))
        self.pb_fetch_pl.setStyleSheet(
            "background-color: #4f46e5; color: #ffffff; font-weight: 600; border: 1px solid #6366f1; padding: 7px 18px; border-radius: 8px;"
        )
        self.pb_fetch_pl.clicked.connect(self.button_fetch_playlist)
        pl_input_layout.addWidget(self.pb_fetch_pl)
        tab_pl_layout.addLayout(pl_input_layout)

        lb_pl_tip = QtWidgets.QLabel(
            "💡 Paste any YouTube playlist URL to preview track numbers, titles, and durations before downloading."
        )
        lb_pl_tip.setStyleSheet("color: #64748b; font-size: 11px;")
        tab_pl_layout.addWidget(lb_pl_tip)

        self.tab_widget.addTab(
            tab_videos, qta.icon("mdi6.video-outline", color="#818cf8"), "Single Video(s)"
        )
        self.tab_widget.addTab(
            tab_playlist, qta.icon("mdi6.playlist-play", color="#818cf8"), "YouTube Playlist"
        )
        card_input_layout.addWidget(self.tab_widget)

        # Options Strip: Destination, Preset, Quality, Add button
        opt_layout = QtWidgets.QHBoxLayout()
        opt_layout.setSpacing(10)

        lb_save = QtWidgets.QLabel("Save to:")
        lb_save.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        opt_layout.addWidget(lb_save)

        self.le_path.setMinimumWidth(180)
        opt_layout.addWidget(self.le_path, 1)

        self.pb_path.setText(" Browse...")
        self.pb_path.setIcon(qta.icon("mdi6.folder-open", color="#cbd5e1"))
        opt_layout.addWidget(self.pb_path)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        sep.setStyleSheet("color: #232b3d; max-width: 1px;")
        opt_layout.addWidget(sep)

        lb_fmt = QtWidgets.QLabel("Format:")
        lb_fmt.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        opt_layout.addWidget(lb_fmt)

        self.dd_preset.setMinimumWidth(100)
        opt_layout.addWidget(self.dd_preset)

        lb_qual = QtWidgets.QLabel("Quality:")
        lb_qual.setStyleSheet("font-weight: 600; color: #cbd5e1;")
        opt_layout.addWidget(lb_qual)

        self.dd_quality.setMinimumWidth(120)
        opt_layout.addWidget(self.dd_quality)

        self.pb_add.setText(" Add to Queue")
        self.pb_add.setIcon(qta.icon("mdi6.plus-circle", color="#ffffff"))
        self.pb_add.setIconSize(QtCore.QSize(18, 18))
        self.pb_add.setStyleSheet(
            "background-color: #059669; color: #ffffff; font-weight: 600; border: 1px solid #10b981; padding: 7px 20px; border-radius: 8px;"
        )
        opt_layout.addWidget(self.pb_add)

        card_input_layout.addLayout(opt_layout)
        root_layout.addWidget(card_input)

        # 3. Card 2: Downloads Queue Card
        card_queue = QtWidgets.QFrame()
        card_queue.setObjectName("card_queue")
        card_queue_layout = QtWidgets.QVBoxLayout(card_queue)
        card_queue_layout.setContentsMargins(12, 12, 12, 12)
        card_queue_layout.setSpacing(8)

        queue_top = QtWidgets.QHBoxLayout()
        lb_q_title = QtWidgets.QLabel("Downloads Queue")
        font_q = QtGui.QFont()
        font_q.setBold(True)
        font_q.setPointSize(10)
        lb_q_title.setFont(font_q)
        lb_q_title.setStyleSheet("color: #cbd5e1;")
        queue_top.addWidget(lb_q_title)

        self.lb_queue_sub = QtWidgets.QLabel("(0 items in queue)")
        self.lb_queue_sub.setStyleSheet("color: #64748b; font-size: 12px;")
        queue_top.addWidget(self.lb_queue_sub)
        queue_top.addStretch(1)

        lb_q_hint = QtWidgets.QLabel("💡 Right-click item to copy link, open folder, or remove")
        lb_q_hint.setStyleSheet("color: #64748b; font-size: 11px;")
        queue_top.addWidget(lb_q_hint)
        card_queue_layout.addLayout(queue_top)

        card_queue_layout.addWidget(self.tw, 1)
        root_layout.addWidget(card_queue, 1)

        # 4. Footer Action Bar
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.setSpacing(12)

        self.lb_footer_status = QtWidgets.QLabel("Ready")
        self.lb_footer_status.setStyleSheet("color: #94a3b8; font-size: 12px;")
        footer_layout.addWidget(self.lb_footer_status)
        footer_layout.addStretch(1)

        self.pb_clear.setText(" Clear List")
        self.pb_clear.setIcon(qta.icon("mdi6.trash-can-outline", color="#f87171"))
        self.pb_clear.setIconSize(QtCore.QSize(18, 18))
        footer_layout.addWidget(self.pb_clear)

        self.pb_download.setText(" Start Download")
        self.pb_download.setIcon(qta.icon("mdi6.download", color="#ffffff"))
        self.pb_download.setIconSize(QtCore.QSize(18, 18))
        self.pb_download.setStyleSheet(
            "background-color: #4f46e5; color: #ffffff; font-weight: 700; border: 1px solid #6366f1; padding: 8px 26px; border-radius: 8px; font-size: 13px;"
        )
        footer_layout.addWidget(self.pb_download)

        root_layout.addLayout(footer_layout)

    def connect_ui(self):
        # buttons
        self.pb_path.clicked.connect(self.button_path)
        self.pb_add.clicked.connect(self.button_add)
        self.pb_clear.clicked.connect(self.button_clear)
        self.pb_download.clicked.connect(self.button_download)

        # combo boxes
        self.dd_preset.currentTextChanged.connect(self.on_preset_changed)

        # menu bar
        self.action_open_bin_folder.triggered.connect(lambda: self.open_folder(BIN_DIR))
        self.action_open_log_folder.triggered.connect(lambda: self.open_folder(LOG_DIR))
        self.action_exit.triggered.connect(self.close)
        self.action_about.triggered.connect(self.show_about)
        self.action_clear_url_list.triggered.connect(self.te_link.clear)

    def on_preset_changed(self, preset_name):
        preset_cmd = self.config["presets"].get(preset_name, "")
        preset_args = preset_cmd if isinstance(preset_cmd, list) else preset_cmd.split()
        is_audio = "--extract-audio" in preset_args or "-x" in preset_args
        self.dd_quality.setEnabled(not is_audio)

    def on_dep_progress(self, status):
        self.statusBar.showMessage(status, 10000)
        if hasattr(self, "badge_status"):
            self.badge_status.setText(f"⚡ {status}")

    def on_dep_finished(self):
        self.dep_worker.deleteLater()
        self.pb_download.setEnabled(True)
        if hasattr(self, "badge_status"):
            self.badge_status.setText("🟢 Ready")
            self.badge_status.setStyleSheet(
                "background-color: #141824; border: 1px solid #10b981; border-radius: 12px; "
                "padding: 5px 14px; color: #34d399; font-weight: 600; font-size: 11px;"
            )

    def open_folder(self, path):
        try:
            path_obj = Path(path)
            path_obj.mkdir(parents=True, exist_ok=True)
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(path_obj)))
        except Exception as e:
            logger.error(f"Error opening folder {path}: {e}")

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self,
            "About YT Video Downloader",
            f'<a href="https://github.com/harshverma-25/yt-video-downloader">YT Video Downloader</a> {__version__}<br><br>'
            "A desktop application for downloading videos and audio using yt-dlp.",
        )

    def button_paste(self):
        clipboard = QtWidgets.QApplication.clipboard().text().strip()
        if clipboard:
            current = self.te_link.toPlainText().strip()
            if current:
                self.te_link.setPlainText(current + "\n" + clipboard)
            else:
                self.te_link.setPlainText(clipboard)
            self.te_link.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    def button_paste_playlist(self):
        clipboard = QtWidgets.QApplication.clipboard().text().strip()
        if clipboard:
            cleaned = clean_and_extract_url(clipboard)
            self.le_playlist.setText(cleaned)

    def button_fetch_playlist(self):
        raw = self.le_playlist.text().strip()
        if not raw:
            raw = self.te_link.toPlainText().strip()
            if raw:
                self.le_playlist.setText(raw)
        url = clean_and_extract_url(raw)
        if url:
            self.le_playlist.setText(url)

        if not url:
            return QtWidgets.QMessageBox.information(
                self,
                "Application Message",
                "Please enter or paste a YouTube playlist URL to fetch videos.",
            )

        if not is_playlist_url(url):
            return QtWidgets.QMessageBox.warning(
                self,
                "Invalid Playlist URL",
                "The provided URL does not appear to be a YouTube playlist.\n\n"
                "Please make sure it contains 'playlist?list=...' or 'list=...'.",
            )

        preset = self.dd_preset.currentText()
        preset_cmd = self.config["presets"].get(preset, "")
        preset_args = (
            preset_cmd if isinstance(preset_cmd, list) else preset_cmd.split()
        )
        is_audio = "--extract-audio" in preset_args or "-x" in preset_args
        quality = "N/A" if is_audio else self.dd_quality.currentText()
        path = self.le_path.text().strip()
        if not path:
            return QtWidgets.QMessageBox.information(
                self,
                "Application Message",
                "Please select a 'Save to' folder before fetching playlist.",
            )
        self._handle_playlist_link(url, preset, quality, path, from_playlist_tab=True)

    def open_menu(self, position):
        menu = QtWidgets.QMenu(self)

        delete_action = menu.addAction(
            qta.icon("mdi6.trash-can", color="#f87171"), "Delete"
        )
        menu.addSeparator()
        copy_url_action = menu.addAction(
            qta.icon("mdi6.content-copy", color="#94a3b8"), "Copy URL"
        )
        copy_title_action = menu.addAction(
            qta.icon("mdi6.format-title", color="#94a3b8"), "Copy Title"
        )
        open_browser_action = menu.addAction(
            qta.icon("mdi6.web", color="#38bdf8"), "Open in Browser"
        )
        open_folder_action = menu.addAction(
            qta.icon("mdi6.folder-open", color="#fbbf24"), "Open Folder"
        )

        item = self.tw.itemAt(position)

        if item:
            item_path = item.data(0, ItemRoles.PathRole)
            item_link = item.data(0, ItemRoles.LinkRole)
            item_title = item.text(TreeColumn.TITLE)
            action = menu.exec(self.tw.viewport().mapToGlobal(position))

            if action == delete_action:
                self.remove_item(item, 0)
            elif action == copy_url_action:
                QtWidgets.QApplication.clipboard().setText(item_link)
                logger.info(f"Copied URL to clipboard: {item_link}")
            elif action == copy_title_action:
                QtWidgets.QApplication.clipboard().setText(item_title)
                logger.info(f"Copied Title to clipboard: {item_title}")
            elif action == open_browser_action:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(item_link))
                logger.info(f"Opened link in browser: {item_link}")
            elif action == open_folder_action:
                self.open_folder(item_path)
                logger.info(f"Opened folder: {item_path}")

    def remove_item(self, item, column):
        item_id = item.data(0, ItemRoles.IdRole)
        item_text = item.text(0)

        logger.debug(f"Removing download ({item_id}): {item_text}")

        if item_id in self.pending_queue:
            self.pending_queue.remove(item_id)

        if worker := self.active_workers.pop(item_id, None):
            worker.stop()
            self._process_download_queue()

        self.to_dl.pop(item_id, None)
        index = self.tw.indexOfTopLevelItem(item)
        if index != -1:
            self.tw.takeTopLevelItem(index)
        self._update_queue_count()

    def button_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a folder",
            self.le_path.text() or QtCore.QDir.homePath(),
            QtWidgets.QFileDialog.Option.ShowDirsOnly,
        )

        if path:
            self.le_path.setText(path)

    def _update_queue_count(self):
        count = self.tw.topLevelItemCount()
        if hasattr(self, "badge_queue_count"):
            self.badge_queue_count.setText(f"{count} Item{'s' if count != 1 else ''}")
        if hasattr(self, "lb_queue_sub"):
            self.lb_queue_sub.setText(f"({count} item{'s' if count != 1 else ''} in queue)")
        if hasattr(self, "gb_downloads"):
            self.gb_downloads.setTitle(
                f"Downloads Queue ({count} item{'s' if count != 1 else ''})"
            )

    def _add_queue_item(
        self, link: str, preset: str, quality: str, path: str, title: str = None
    ):
        display_title = title if title else link
        item = QtWidgets.QTreeWidgetItem(
            self.tw, [display_title, preset, quality, "-", "", "Queued", "-", "-"]
        )
        item.setForeground(TreeColumn.STATUS, QtGui.QBrush(QtGui.QColor("#94a3b8")))
        pb = QtWidgets.QProgressBar()
        pb.setTextVisible(False)
        self.tw.setItemWidget(item, TreeColumn.PROGRESS, pb)
        for i in range(1, 8):
            item.setTextAlignment(i, QtCore.Qt.AlignmentFlag.AlignCenter)

        item.setData(0, ItemRoles.IdRole, self.index)
        item.setData(0, ItemRoles.LinkRole, link)
        item.setData(0, ItemRoles.PathRole, path)

        worker = DownloadWorker(item, self.config, link, path, preset, quality)
        self.to_dl[self.index] = worker
        logger.info(
            f"Queued download ({self.index}) added {link} [Title: {display_title}, Preset: {preset}, Quality: {quality}]"
        )
        self.index += 1
        self._update_queue_count()

    def _handle_playlist_link(
        self, link: str, preset: str, quality: str, path: str, from_playlist_tab: bool = False
    ):
        # Prompt if it's a single video watch link that also has &list= (only when not explicitly on playlist tab)
        if not from_playlist_tab and "watch?" in link and "list=" in link:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Playlist Detected")
            msg_box.setIcon(QtWidgets.QMessageBox.Icon.Question)
            msg_box.setText(
                "This link contains a playlist.\n\n"
                "Would you like to view the playlist to select videos, or download only this single video?"
            )
            btn_playlist = msg_box.addButton(
                "Open Playlist", QtWidgets.QMessageBox.ButtonRole.AcceptRole
            )
            btn_single = msg_box.addButton(
                "Single Video Only", QtWidgets.QMessageBox.ButtonRole.RejectRole
            )
            btn_cancel = msg_box.addButton(
                "Cancel", QtWidgets.QMessageBox.ButtonRole.DestructiveRole
            )
            msg_box.exec()

            if msg_box.clickedButton() == btn_cancel:
                return
            elif msg_box.clickedButton() == btn_single:
                clean_url = link.split("&list=")[0].split("?list=")[0]
                self._add_queue_item(clean_url, preset, quality, path)
                return

        # Show clean modal loading dialog
        loading = QtWidgets.QDialog(self)
        loading.setWindowTitle("Loading Playlist")
        loading.setFixedSize(390, 140)
        loading.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)

        loading_layout = QtWidgets.QVBoxLayout(loading)
        loading_layout.setContentsMargins(18, 16, 18, 16)
        loading_layout.setSpacing(10)

        lb_status = QtWidgets.QLabel(
            "Fetching playlist videos from YouTube...\nPlease wait a moment."
        )
        lb_status.setStyleSheet("color: #f1f5f9; font-weight: 500;")
        loading_layout.addWidget(lb_status)

        pb_loading = QtWidgets.QProgressBar()
        pb_loading.setRange(0, 0)
        loading_layout.addWidget(pb_loading)

        btn_cancel_load = QtWidgets.QPushButton("Cancel")
        btn_cancel_load.setFixedWidth(80)
        btn_cancel_load.clicked.connect(loading.reject)
        loading_layout.addWidget(
            btn_cancel_load, 0, QtCore.Qt.AlignmentFlag.AlignRight
        )

        worker = PlaylistFetchWorker(link)
        fetch_result = {}

        def on_finished(data):
            fetch_result["data"] = data
            loading.accept()

        def on_error(err):
            fetch_result["error"] = err
            loading.reject()

        worker.finished.connect(on_finished)
        worker.error.connect(on_error)
        worker.start()

        res = loading.exec()

        if res != QtWidgets.QDialog.DialogCode.Accepted:
            worker.cancel()
            worker.wait(2000)
            if "error" in fetch_result:
                return QtWidgets.QMessageBox.warning(
                    self,
                    "Playlist Error",
                    f"Unable to fetch playlist videos:\n\n{fetch_result['error']}",
                )
            return

        worker.wait(1000)
        data = fetch_result.get("data")
        if not data or not data.get("entries"):
            return QtWidgets.QMessageBox.information(
                self,
                "Empty Playlist",
                "No downloadable videos were found in this playlist.",
            )

        dlg = PlaylistDialog(
            self,
            data,
            self.config["presets"],
            default_preset=preset,
            default_quality=quality,
        )
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            selected_videos = dlg.get_selected_videos()
            chosen_preset = dlg.get_preset()
            chosen_quality = dlg.get_quality()

            if not selected_videos:
                return QtWidgets.QMessageBox.information(
                    self,
                    "No Videos Selected",
                    "No videos were selected for download.",
                )

            for video in selected_videos:
                self._add_queue_item(
                    video["url"],
                    chosen_preset,
                    chosen_quality,
                    path,
                    title=video["title"],
                )

            pl_title = data.get("title") or "Playlist"
            self.statusBar.showMessage(
                f"Added {len(selected_videos)} videos from '{pl_title}'", 8000
            )

    def button_add(self):
        # If user is on the YouTube Playlist tab, run the playlist fetcher
        if hasattr(self, "tab_widget") and self.tab_widget.currentIndex() == 1:
            return self.button_fetch_playlist()

        missing = []
        preset = self.dd_preset.currentText()
        preset_cmd = self.config["presets"].get(preset, "")
        preset_args = (
            preset_cmd if isinstance(preset_cmd, list) else preset_cmd.split()
        )
        is_audio = "--extract-audio" in preset_args or "-x" in preset_args
        quality = "N/A" if is_audio else self.dd_quality.currentText()
        links = self.te_link.toPlainText().strip()
        path = self.le_path.text().strip()

        if not links:
            missing.append("Video URL")
        if not path:
            missing.append("Save to")

        if missing:
            missing_fields = ", ".join(missing)
            return QtWidgets.QMessageBox.information(
                self,
                "Application Message",
                f"Required field{'s' if len(missing) > 1 else ''} ({missing_fields}) missing.",
            )

        self.te_link.clear()

        lines = [clean_and_extract_url(l) for l in links.splitlines() if l.strip()]
        for link in lines:
            if not link:
                continue
            if is_playlist_url(link):
                self._handle_playlist_link(link, preset, quality, path)
            else:
                self._add_queue_item(link, preset, quality, path)

    def button_clear(self):
        active_running = [w for w in self.active_workers.values() if w.isRunning()]
        if active_running:
            return QtWidgets.QMessageBox.critical(
                self,
                "Application Message",
                "Unable to clear list because there are active downloads in progress.\n\n"
                "You can stop or remove an individual download by right-clicking on it and selecting 'Delete'.",
            )

        self.active_workers.clear()
        self.pending_queue.clear()
        self.to_dl.clear()
        self.tw.clear()
        self._update_queue_count()

    def button_download(self):
        # If user has text in Single Video box, queue it first
        if self.te_link.toPlainText().strip():
            self.button_add()

        # If on playlist tab and user typed a playlist link, fetch it
        if hasattr(self, "tab_widget") and self.tab_widget.currentIndex() == 1:
            if self.le_playlist.text().strip() and not self.to_dl and not self.active_workers:
                return self.button_fetch_playlist()

        if not self.to_dl and not self.active_workers and not self.pending_queue:
            return QtWidgets.QMessageBox.information(
                self,
                "Application Message",
                "Unable to download because there are no links in the queue.\n\n"
                "Please add one or more video links or a playlist first.",
            )

        # Enqueue all unstarted workers
        for idx in list(self.to_dl.keys()):
            if idx not in self.pending_queue:
                self.pending_queue.append(idx)

        self._process_download_queue()

    def _process_download_queue(self):
        """Manage concurrency: keep up to MAX_CONCURRENT_DOWNLOADS running."""
        while (
            len(self.active_workers) < self.MAX_CONCURRENT_DOWNLOADS
            and self.pending_queue
        ):
            idx = self.pending_queue.pop(0)
            worker = self.to_dl.pop(idx, None)
            if not worker:
                continue

            self.active_workers[idx] = worker
            worker.finished.connect(worker.deleteLater)
            worker.finished.connect(lambda x=idx: self._on_worker_finished(x))
            worker.progress.connect(self.on_dl_progress)
            worker.start()

        if hasattr(self, "lb_footer_status"):
            active_count = len(self.active_workers)
            queue_count = len(self.pending_queue)
            if active_count > 0:
                self.lb_footer_status.setText(f"⚡ Downloading: {active_count} active • {queue_count} pending")
            elif queue_count > 0:
                self.lb_footer_status.setText(f"Queued: {queue_count} item{'s' if queue_count != 1 else ''}")
            else:
                self.lb_footer_status.setText("Ready")

    def _on_worker_finished(self, idx):
        self.active_workers.pop(idx, None)
        self._process_download_queue()
        if not self.active_workers and not self.pending_queue:
            self.statusBar.showMessage("All downloads completed!", 8000)
            if hasattr(self, "lb_footer_status"):
                self.lb_footer_status.setText("✓ All downloads completed!")

    def load_config(self):
        config_path = get_config_path()
        template_config_path = get_resource_path("config.toml")

        default_config = {
            "general": {
                "current_preset": 0,
                "current_quality": 0,
                "path": get_default_download_dir(),
                "global_args": "",
                "update_ytdlp": True,
            },
            "presets": {
                "best": "-f bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
                "mp4": "-f bv*[vcodec^=avc]+ba[ext=m4a]/b",
                "mp3": "--extract-audio --audio-format mp3 --audio-quality 0",
            },
        }

        try:
            if not config_path.exists():
                if template_config_path.exists():
                    try:
                        self.config = load_toml(template_config_path)
                    except Exception:
                        self.config = default_config
                else:
                    self.config = default_config
                save_toml(config_path, self.config)
            else:
                self.config = load_toml(config_path)
        except Exception as e:
            logger.error(f"Error loading config, using defaults: {e}", exc_info=True)
            self.config = default_config

        if "general" not in self.config:
            self.config["general"] = default_config["general"]
        if "presets" not in self.config:
            self.config["presets"] = default_config["presets"]

        update_ytdlp = self.config["general"].get("update_ytdlp", True)
        self.config["general"]["update_ytdlp"] = bool(update_ytdlp)

        self.dd_preset.clear()
        self.dd_preset.addItems(list(self.config["presets"].keys()))
        current_preset = self.config["general"].get("current_preset", 0)
        if isinstance(current_preset, int) and 0 <= current_preset < self.dd_preset.count():
            self.dd_preset.setCurrentIndex(current_preset)

        self.dd_quality.clear()
        self.dd_quality.addItems(QUALITY_OPTIONS)
        current_quality = self.config["general"].get("current_quality", 0)
        if (
            isinstance(current_quality, int)
            and 0 <= current_quality < self.dd_quality.count()
        ):
            self.dd_quality.setCurrentIndex(current_quality)

        saved_path = self.config["general"].get("path", "")
        if not saved_path or not Path(saved_path).exists():
            saved_path = get_default_download_dir()
        self.le_path.setText(saved_path)
        self.on_preset_changed(self.dd_preset.currentText())

    def closeEvent(self, event):
        # Stop active workers cleanly to avoid orphan subprocesses or Qt thread crashes
        for worker in list(self.active_workers.values()):
            if worker.isRunning():
                worker.stop()
                worker.wait(2000)

        if hasattr(self, "dep_worker") and self.dep_worker.isRunning():
            self.dep_worker.wait(3000)

        try:
            self.config["general"]["current_preset"] = self.dd_preset.currentIndex()
            self.config["general"]["current_quality"] = self.dd_quality.currentIndex()
            self.config["general"]["path"] = self.le_path.text()
            save_toml(get_config_path(), self.config)
        except Exception as e:
            logger.error(f"Error saving config on close: {e}")

        event.accept()

    def on_dl_progress(self, item: QtWidgets.QTreeWidgetItem, emit_data):
        try:
            for data in emit_data:
                index, update = data
                if index != TreeColumn.PROGRESS:
                    item.setText(index, update)
                    if index == TreeColumn.STATUS:
                        status_lower = update.lower()
                        if "finished" in status_lower:
                            item.setForeground(
                                index, QtGui.QBrush(QtGui.QColor("#34d399"))
                            )
                        elif "download" in status_lower:
                            item.setForeground(
                                index, QtGui.QBrush(QtGui.QColor("#38bdf8"))
                            )
                        elif (
                            "converting" in status_lower
                            or "processing" in status_lower
                        ):
                            item.setForeground(
                                index, QtGui.QBrush(QtGui.QColor("#c084fc"))
                            )
                        elif "error" in status_lower:
                            item.setForeground(
                                index, QtGui.QBrush(QtGui.QColor("#f87171"))
                            )
                        else:
                            item.setForeground(
                                index, QtGui.QBrush(QtGui.QColor("#94a3b8"))
                            )
                else:
                    pb = self.tw.itemWidget(item, index)
                    if pb:
                        try:
                            clean_val = update.replace("%", "").strip()
                            pb.setValue(round(float(clean_val)))
                        except ValueError:
                            pass
        except (AttributeError, RuntimeError):
            # Widget or item was already removed or destroyed
            pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
