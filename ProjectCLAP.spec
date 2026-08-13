# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files


root = Path(SPEC).resolve().parent
datas = []
binaries = []
hiddenimports = []

for package in (
    "openwakeword",
    "onnxruntime",
    "pygame",
    "pystray",
    "PIL",
    "speech_recognition",
    "sounddevice",
    "bleak",
    "googleapiclient",
    "google_auth_oauthlib",
    "edge_tts",
    "pycaw",
):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

# Package only explicitly approved public resources.  Never sweep whole folders:
# those folders can also contain ignored, user-local files such as briefing music
# or candidate models.
for relative_path in (
    "models/wake_words/approved/hey_Clap_20260813.onnx",
    "models/wake_words/hey_Clap.onnx",
    "models/wake_words/hey_Clap.onnx.data",
):
    source = root / relative_path
    datas.append((str(source), str(Path(relative_path).parent)))
for example in (root / "config").glob("*.example.json"):
    datas.append((str(example), "config"))

a = Analysis(
    [str(root / "src" / "clap_tray.py")],
    pathex=[str(root / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ProjectCLAP",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ProjectCLAP",
)
