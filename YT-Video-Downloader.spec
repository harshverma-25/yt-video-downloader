# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Base path
SPECPATH = Path('.').resolve()

# App entrypoint
entrypoint = str(SPECPATH / 'app' / 'app.py')

# Assets and data files to bundle
datas = [
    (str(SPECPATH / 'app' / 'assets'), 'assets'),
    (str(SPECPATH / 'app' / 'assets'), 'app/assets'),
    (str(SPECPATH / 'app' / 'ui'), 'ui'),
    (str(SPECPATH / 'app' / 'ui'), 'app/ui'),
    (str(SPECPATH / 'app' / 'config.toml'), '.'),
    (str(SPECPATH / 'app' / 'config.toml'), 'app'),
    (str(SPECPATH / 'LICENSE'), '.'),
]

# Add any additional data files from qtawesome
datas += collect_data_files('qtawesome')

# Hidden imports
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'qtawesome',
    'platformdirs',
    'tomlkit',
    'requests',
    'urllib.parse',
    'json',
    'shlex',
    'subprocess',
    'platform',
    'shutil',
    'stat',
    'zipfile',
]
hiddenimports += collect_submodules('qtawesome')

a = Analysis(
    [entrypoint],
    pathex=[str(SPECPATH / 'app'), str(SPECPATH)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas', 'unittest', 'test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YT-Video-Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(SPECPATH / 'app' / 'assets' / 'yt-video-downloader.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='YT-Video-Downloader',
)
