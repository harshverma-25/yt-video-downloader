# YT Video Downloader

A simple desktop app for downloading videos and audio, built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

[![Release](https://img.shields.io/github/v/release/harshverma-25/yt-video-downloader?include_prereleases&style=flat-square)](https://github.com/harshverma-25/yt-video-downloader/releases)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg?style=flat-square)](https://unlicense.org/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

## Features

- **Modern dark UI** built with PySide6 (Qt).
- **Quality choice**: 144p up to 8K, or best available.
- **Playlist support**: fetch a playlist, search/filter it, and download all or selected videos.
- **Audio extraction**: convert to MP3.
- **Download queue**: queue many links and track progress, speed, size, and ETA.
- **Fast downloads**: multi-connection fragments, HTTP chunking, and a large I/O buffer.
- **Custom presets**: edit `config.toml` to add your own formats.
- **Auto setup**: downloads `yt-dlp`, `ffmpeg`, `ffprobe`, and `deno` on first launch.

## Install (Windows)

Download from [GitHub Releases](https://github.com/harshverma-25/yt-video-downloader/releases). No Python needed.

| Version | File | Links |
|---|---|---|
| Installer (recommended) | `YT-Video-Downloader-Setup.exe` | https://github.com/harshverma-25/yt-video-downloader/actions/runs/45418797671/artifacts/14932963200 |
| Portable | `YT-Video-Downloader-Portable.zip` | https://github.com/harshverma-25/yt-video-downloader/actions/runs/45418797671/artifacts/14932868368 |

## Usage

**Single videos**
1. Paste one or more URLs in the **Single Video(s)** tab.
2. Pick a save folder, preset (`best`, `mp4`, `mp3`), and quality.
3. Click **Add to Queue**, then **Start Download**.

**Playlists**
1. Open the **YouTube Playlist** tab and paste the playlist link.
2. Click **Fetch Playlist Videos**.
3. Filter, select videos, then click **Download Selected** or **Download All**.
4. Click **Start Download**.

## Run from Source

Requires Python 3.9+ on Windows, Linux, or macOS.

```bash
git clone https://github.com/harshverma-25/yt-video-downloader.git
cd yt-video-downloader

python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
cd app
python app.py
```

## Build

Requires `pyinstaller` and, for the installer, [Inno Setup 6](https://jrsoftware.org/isdl.php).

```bash
# Standalone folder (output: dist/YT-Video-Downloader/)
pyinstaller YT-Video-Downloader.spec --noconfirm --clean
```

```powershell
# Portable ZIP
New-Item -ItemType File -Path "dist\YT-Video-Downloader\portable.txt" -Force
Copy-Item "README-PORTABLE.txt" "dist\YT-Video-Downloader\" -Force
Compress-Archive -Path "dist\YT-Video-Downloader" -DestinationPath "dist\YT-Video-Downloader-Portable.zip" -Force

# Installer (output: dist/installer/YT-Video-Downloader-Setup.exe)
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

## Project Structure

```
app/
├── app.py              # Main window and controller
├── worker.py           # Download worker
├── playlist_dialog.py  # Playlist selection dialog
├── dep_dl.py           # Dependency downloader
├── utils.py            # Paths, enums, helpers
├── style.py            # Dark theme
├── config.toml         # Settings and presets
├── ui/                 # Qt Designer UI files
└── assets/             # Icons
.github/workflows/release.yaml   # Automated releases
```

## Tech Stack

PySide6 · yt-dlp · FFmpeg/FFprobe · Deno · QtAwesome · tomlkit · PyInstaller

## License

Released under [The Unlicense](LICENSE) (public domain). Forked from work by `dsymbol` and now maintained independently. Downloading is powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp), FFmpeg, and Deno.
