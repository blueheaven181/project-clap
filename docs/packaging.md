# Project CLAP Windows Packaging

Project CLAP uses a PyInstaller one-folder build. This layout is preferred over
one-file extraction because CLAP depends on native audio, ONNX Runtime,
Bluetooth, GUI, and wake-model resources.

## Build tool

Install the pinned build-only dependency:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
```

Build from the repository root:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean ProjectCLAP.spec
```

The output is written to `dist/ProjectCLAP/`. Build output is not source and
must not be committed.

## Privacy boundary

The specification includes public assets, approved project models, and example
configuration only. It must never include `config/*.local.json`, Google
credentials or tokens, private recordings, private profiles, local logs, or
device identifiers.

Packaged CLAP reads mutable and private files from:

```text
%LOCALAPPDATA%\ProjectCLAP
```

Development runs continue to use the repository paths. Before the first real
packaged run, copy only the approved private files without overwriting existing
installed data:

```powershell
.\.venv\Scripts\python.exe .\src\migrate_packaged_data.py
```

## Safe first smoke test

Run the packaged tray preview without starting the listener:

```powershell
.\dist\ProjectCLAP\ProjectCLAP.exe --preview
```

The real listener lifecycle is tested only after packaged runtime paths and
private-data migration have been validated. Never distribute the
`%LOCALAPPDATA%\ProjectCLAP` folder with the public application package.
