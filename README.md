# YT Video Downloader

YT Video Downloader is a modern, high-speed Windows desktop application providing an intuitive graphical interface for downloading single videos, audio tracks, and full playlists powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp), [FFmpeg](https://ffmpeg.org/), and [Deno](https://deno.land/).

[![GitHub release](https://img.shields.io/github/v/release/harshverma-25/yt-video-downloader?include_prereleases&style=flat-square)](https://github.com/harshverma-25/yt-video-downloader/releases)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg?style=flat-square)](https://unlicense.org/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Platform: Windows 10 / 11](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-blue.svg?style=flat-square)](https://github.com/harshverma-25/yt-video-downloader/releases)

---

## Download & Installation (Windows)

No Python, Git, or development environment required! Pre-compiled, standalone Windows 64-bit binaries are available for every release on [GitHub Releases](https://github.com/harshverma-25/yt-video-downloader/releases).

### 1. Windows Installer (`YT-Video-Downloader-Setup.exe`)
- **Direct Download**: [**Download Latest Setup.exe**](https://github.com/harshverma-25/yt-video-downloader/releases/latest/download/YT-Video-Downloader-Setup.exe)
- Standard Windows wizard installer.
- Automatically creates Start Menu and Desktop shortcuts.
- Stores user configuration and downloaded tools in `%LOCALAPPDATA%\yt-video-downloader`.
- Installs with user privileges (no Administrator UAC elevation required).
- Includes clean Windows Uninstaller registered in Windows Settings (Add or Remove Programs).

### 2. Portable Version (`YT-Video-Downloader-Portable.zip`)
- **Direct Download**: [**Download Latest Portable.zip**](https://github.com/harshverma-25/yt-video-downloader/releases/latest/download/YT-Video-Downloader-Portable.zip)
- Zero installation required: extract the ZIP file anywhere (e.g. USB flash drive, external drive).
- All settings, history, and backend dependencies are kept strictly inside the local `data/` subfolder.
- Completely isolated: leaves zero registry keys or AppData files on the host PC.
- Simply delete or move the extracted folder to uninstall or migrate.

### Edition Comparison

| Feature | Windows Setup Installer | Portable Edition |
|---|---|---|
| **File Type** | `.exe` wizard installer | `.zip` archive |
| **Admin Rights** | Not required | Not required |
| **Shortcut Creation** | Desktop & Start Menu | None (run directly) |
| **Settings Location** | `%LOCALAPPDATA%\yt-video-downloader` | `<folder>\data\` |
| **Dependency Binaries** | `%LOCALAPPDATA%\yt-video-downloader\bin` | `<folder>\data\bin\` |
| **Registry Footprint** | Windows Add/Remove entry | Completely clean (0 registry entries) |
| **Best For** | Primary desktop PC | USB drives, shared computers |

---

## Features

- **Intuitive Graphical Interface**: Clean, dark theme built with PySide6 (Qt) designed for clarity and efficiency.
- **Resolution & Quality Selection**: Download in your exact desired resolution: 8K (`4320p`), 4K (`2160p`), 2K (`1440p`), `1080p`, `720p`, `480p`, `360p`, `240p`, `144p`, or `Best` available.
- **Dedicated YouTube Playlist Inspector**:
  - Automatically fetches all videos in any YouTube playlist link.
  - Interactive table displaying track numbers, video titles, and formatted durations.
  - Quick filter/search box to instantly locate specific tracks.
  - Select individual videos or use **Select All** / **Deselect All**.
  - Direct enqueueing into the batch queue with human-readable titles.
- **Maximum Download Speeds**:
  - Accelerated multi-connection downloading using 8 concurrent fragment streams (`-N 8`).
  - HTTP chunking (`--http-chunk-size 10M`) to bypass platform-side bandwidth throttling.
  - 1MB buffer size (`--buffer-size 1024k`) for optimal disk I/O throughput.
- **High-Quality Audio Extraction**: One-click audio conversion directly to MP3 (VBR 0 / ~320 kbps).
- **Batch Download Queue**: Concurrently download multiple links with real-time transfer speeds, progress percentages, estimated time of arrival (ETA), and total file sizes.
- **Automatic Dependency Setup**:
  - Automatically downloads required backend binaries (`yt-dlp`, `ffmpeg`, `ffprobe`, `deno`) on startup into the mode-specific binary folder.
  - Verifies SHA-256 hashes on immutable assets and validates ZIP extraction integrity.
  - Completely self-updating for `yt-dlp` (`yt-dlp -U`).

---

## First-Launch Dependency Setup

On first launch, YT Video Downloader checks for the required download tools:
1. `yt-dlp`: The core extraction and download engine.
2. `ffmpeg` & `ffprobe`: Media stream multiplexer, audio extractor, and converter.
3. `deno`: Fast JavaScript runtime enabling yt-dlp to solve modern video stream client challenges.

If any tool is missing, the application automatically downloads it in the background using HTTPS into the appropriate directory (`%LOCALAPPDATA%\yt-video-downloader\bin` in installed mode, or `<app_dir>\data\bin` in portable mode). Fixed binaries are verified against known SHA-256 hashes, and ZIP archives are extracted safely with Zip-Slip path-traversal safeguards.

---

## System Requirements

- **Operating System**: Windows 10 (64-bit) or Windows 11 (64-bit)
- **Architecture**: x64 (64-bit Intel/AMD)
- **Network**: Active internet connection for downloading media and initial backend tools.

---

## Usage Instructions

### Downloading Single Videos
1. Launch **YT Video Downloader**.
2. In the **Single Video(s)** tab, paste one or more URLs into the text area (one per line).
3. Select your output folder with **Browse...**.
4. Select your **Preset** (`best`, `mp4`, `mp3`) and target **Quality** (e.g., `1080p`).
5. Click **Add to Queue**.
6. Click **Start Download**.

### Downloading Playlists
1. Navigate to the **YouTube Playlist** tab.
2. Paste the playlist link (e.g. `https://www.youtube.com/playlist?list=...`).
3. Click **Fetch Playlist Videos** (or press <kbd>Enter</kbd>).
4. Review the playlist tracks, filter by search keyword, or toggle selections.
5. Click **Download Selected** or **Download All**.
6. Click **Start Download** in the main window.

---

## Troubleshooting

### Windows SmartScreen Warning on First Launch
- Because the executable is built without an expensive enterprise EV certificate, Windows Defender SmartScreen may display: *"Windows protected your PC"*.
- Click **More info**, then click **Run anyway**. The code is 100% open source under The Unlicense and the complete build process is transparent in [GitHub Actions](https://github.com/harshverma-25/yt-video-downloader/actions).

### Dependency Check Failed or Offline Mode
- If you start the app without internet access on a fresh computer, the app displays: `⚠️ Missing dependencies. Connect to internet to download.`
- Connect to the internet and restart the application to let it download `yt-dlp`, `ffmpeg`, and `deno`. Once downloaded, internet access is only needed for video links.

### Audio Extraction (MP3) Fails
- Ensure FFmpeg has finished downloading. Check the menu bar: **Tools** > **Open Binaries Folder** to verify `ffmpeg.exe` and `ffprobe.exe` are present.

### Viewing Application Logs
- In the top menu bar, select **Help** > **Open Log Folder** to view `debug.log`.

---

## Development Setup (Run from Source)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/harshverma-25/yt-video-downloader.git
   cd yt-video-downloader
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch application**:
   ```bash
   cd app
   python app.py
   ```

---

## Packaging & Building

### Prerequisites
- Python 3.9+ with `requirements.txt` and `pyinstaller` installed (`pip install pyinstaller`)
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (for compiling the installer)

### 1. Build Standalone Folder with PyInstaller
```bash
pyinstaller YT-Video-Downloader.spec --noconfirm --clean
```
The output directory will be placed in `dist/YT-Video-Downloader/` containing `YT-Video-Downloader.exe`.

### 2. Create Portable ZIP
```powershell
New-Item -ItemType File -Path "dist\YT-Video-Downloader\portable.txt" -Force
Copy-Item -Path "README-PORTABLE.txt" -Destination "dist\YT-Video-Downloader\" -Force
Compress-Archive -Path "dist\YT-Video-Downloader" -DestinationPath "dist\YT-Video-Downloader-Portable.zip" -Force
Remove-Item -Path "dist\YT-Video-Downloader\portable.txt" -Force
```

### 3. Build Windows Installer (`.exe`) with Inno Setup
```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion="1.0.0" installer\setup.iss
```
The installer executable will be generated at `dist/installer/YT-Video-Downloader-Setup.exe`.

---

## Project Structure

```
yt-video-downloader/
├── .github/
│   └── workflows/
│       └── release.yaml       # GitHub Actions automated release workflow
├── app/
│   ├── assets/
│   │   ├── yt-video-downloader.ico  # Application icon
│   │   └── yt-dlp-gui.ico           # Legacy icon asset
│   ├── ui/
│   │   ├── main_window.ui     # Qt Designer interface definition
│   │   └── main_window.py     # Compiled Qt UI class
│   ├── app.py                 # Main application window and controller
│   ├── config.toml            # User configuration and presets
│   ├── dep_dl.py              # Automatic binary dependency manager
│   ├── playlist_dialog.py     # Playlist inspection and batch selection dialog
│   ├── style.py               # Modern dark theme stylesheet
│   ├── utils.py               # Path definitions, enums, helper functions
│   ├── version.py             # Central single source of truth for versioning
│   └── worker.py              # Multi-fragment download worker
├── installer/
│   └── setup.iss              # Inno Setup Windows installer compiler script
├── LICENSE                    # The Unlicense
├── README-PORTABLE.txt        # Documentation bundled inside Portable ZIP
├── README.md                  # Comprehensive project documentation
├── requirements.txt           # Python dependencies
└── YT-Video-Downloader.spec   # PyInstaller onedir specification
```

---

## License & Attribution

This project is released into the public domain under the terms of **The Unlicense**. You are free to copy, modify, publish, use, compile, sell, or distribute this software for any purpose.

- Underlying download capabilities powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).
- Binary distribution relies on [FFmpeg](https://ffmpeg.org/) and [Deno](https://deno.land/).
- Originally forked and customized from open-source work by `dsymbol`, now maintained as an independent project.

See the [LICENSE](LICENSE) file for the complete license text.

---

## Repository

- **GitHub Repository**: [https://github.com/harshverma-25/yt-video-downloader](https://github.com/harshverma-25/yt-video-downloader)
- **Releases**: [https://github.com/harshverma-25/yt-video-downloader/releases](https://github.com/harshverma-25/yt-video-downloader/releases)
