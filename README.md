# YT Video Downloader

YT Video Downloader is a desktop application that provides a graphical interface for downloading videos and audio using yt-dlp.

[![GitHub release](https://img.shields.io/github/v/release/harshverma-25/yt-video-downloader?include_prereleases&style=flat-square)](https://github.com/harshverma-25/yt-video-downloader/releases)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg?style=flat-square)](https://unlicense.org/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

---

## Features

- **Intuitive Graphical Interface**: Clean, modern dark theme built with PySide6 (Qt) designed for ease of use.
- **Quality Selection**: Download videos in your preferred resolution, from standard definition (144p, 360p, 480p, 720p) up to high resolution (1080p, 1440p 2K, 2160p 4K, 4320p 8K) or Best available quality.
- **Dedicated YouTube Playlist Downloader**:
  - Automatically fetches and displays all videos in a playlist.
  - Interactive selection table with track numbers, full titles, and formatted durations.
  - Search/filter capability to find specific videos instantly.
  - Options to download all videos or selectively download specific tracks.
  - Intelligent handling of watch links that contain playlist parameters.
- **Maximum Download Speeds**:
  - Accelerated multi-connection downloading using 8 concurrent fragment streams (`-N 8`).
  - HTTP chunking (`--http-chunk-size 10M`) to bypass platform-side bandwidth throttling.
  - 1MB buffer size (`--buffer-size 1024k`) for high-throughput disk I/O.
- **Audio Extraction**: Easily extract and convert audio to MP3 with high-quality bitrate settings.
- **Configurable Presets**: Modify or create custom presets in `config.toml` (e.g., MP4 format, MP3 audio, custom format strings).
- **Batch Download Queue**: Queue multiple video and playlist links, monitor individual download progress, transfer speeds, file sizes, and estimated time of arrival (ETA).
- **Automatic Dependency Setup**: Checks, downloads, and configures required backend binaries (`yt-dlp`, `ffmpeg`, `ffprobe`, `deno`) on startup without manual intervention.

---

## Screenshots

> _Placeholder: Main Window and Playlist Inspector Screenshots_

```
+---------------------------------------------------------------------------------+
|  YT Video Downloader                                                   [-] [x]  |
+---------------------------------------------------------------------------------+
| [ Parameters / URL Input ]                                                      |
|   Tabs: [ Single Video(s) ] [ YouTube Playlist ]                                |
|   Video URL(s): [ https://www.youtube.com/watch?v=...             ]            |
|   Save to:      [ C:/Users/.../Downloads       ] [ Browse... ]                  |
|   Preset: [ Best |v]   Quality: [ 1080p |v]   [ + Add to Queue ]                |
+---------------------------------------------------------------------------------+
| [ Downloads Queue (3 items) ]                                                   |
|   Title                      | Preset | Quality | Progress | Status     | Speed |
|   Lesson 1: Introduction     | best   | 1080p   | [======] | Finished   | -     |
|   Lesson 2: Core Concepts    | best   | 1080p   | [===>  ] | 18.2 MiB/s | 00:15 |
|   Lesson 3: Advanced Topics  | best   | 1080p   | [      ] | Queued     | -     |
+---------------------------------------------------------------------------------+
|                                          [ Clear List ]   [ Start Download ]    |
+---------------------------------------------------------------------------------+
```

---

## Technology Stack

- **GUI Framework**: [PySide6](https://wiki.qt.io/Qt_for_Python) (Qt 6 for Python)
- **Core Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Media Post-Processing**: [FFmpeg](https://ffmpeg.org/) and [FFprobe](https://ffmpeg.org/ffprobe.html)
- **JavaScript Engine**: [Deno](https://deno.land/) (for fast client challenge solving)
- **Iconography**: [QtAwesome](https://github.com/spyder-ide/qtawesome) (Material Design Icons)
- **Configuration**: [tomlkit](https://github.com/sdispater/tomlkit)
- **Packaging & Builds**: [PyInstaller](https://pyinstaller.org/)

---

## Installation & Prerequisites

### Prerequisites

- **Python**: Version 3.9 or newer (Python 3.10+ recommended)
- **Operating System**: Windows 10/11, Linux, or macOS

### Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

*Note: On startup, the application automatically verifies and downloads necessary binary helpers (`yt-dlp`, `ffmpeg`, `ffprobe`, `deno`) into the local application data directory if they are not already installed on your system.*

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/harshverma-25/yt-video-downloader.git
   cd yt-video-downloader
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   cd app
   python app.py
   ```

---

## Usage Instructions

### Downloading Single Videos
1. Open the application.
2. In the **Single Video(s)** tab, paste one or more video URLs into the text area.
3. Choose your desired output directory using **Browse...**.
4. Select your **Preset** (`best`, `mp4`, `mp3`) and target **Quality** (e.g., `1080p`, `720p`, `4K`).
5. Click **Add to Queue**.
6. Click **Start Download**.

### Downloading Playlists
1. Navigate to the **YouTube Playlist** tab.
2. Paste the playlist link (e.g., `https://www.youtube.com/playlist?list=...`).
3. Click **Fetch Playlist Videos** (or press <kbd>Enter</kbd>).
4. The playlist window will display all videos with their duration and track number.
5. Filter by keyword, check individual items, or use **Select All** / **Deselect All**.
6. Click **Download Selected** or **Download All** to add them to your queue with human-readable titles.
7. Click **Start Download**.

---

## Building an Executable

To create a standalone portable executable on Windows using PyInstaller:

```bash
cd app
pyinstaller --name=yt-video-downloader --clean -y app.py --icon ./assets/yt-video-downloader.ico --add-data "config.toml;." --add-data "assets;assets" --noconsole
```

The resulting standalone application will be located in the `app/dist/yt-video-downloader/` directory.

---

## Running Tests

Execute the automated test suite with Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

All 16 unit and integration tests cover URL sanitization, playlist parsing, duration formatting, path resolution, configuration loading, and yt-dlp argument generation.

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
│   └── worker.py              # Asynchronous multi-fragment download worker
├── tests/                     # Automated unit and integration test suite
│   ├── test_config.py         # Configuration file handling and defaults tests
│   ├── test_playlist.py       # URL sanitation and duration formatting tests
│   ├── test_utils.py          # Binary discovery and path tests
│   └── test_worker.py         # yt-dlp argument builder and speed tests
├── LICENSE                    # The Unlicense
├── README.md                  # Project documentation
└── requirements.txt           # Python package dependencies
```

---

## License & Attribution

This project is released into the public domain under the terms of **The Unlicense**. You are free to copy, modify, publish, use, compile, sell, or distribute this software for any purpose.

- Underlying download capabilities powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).
- Binary distribution relies on FFmpeg and Deno.
- Originally forked and customized from open-source work by `dsymbol`, now maintained as an independent project.

See the [LICENSE](LICENSE) file for the complete license text.

---

## Repository

- **GitHub Repository**: [https://github.com/harshverma-25/yt-video-downloader](https://github.com/harshverma-25/yt-video-downloader)

