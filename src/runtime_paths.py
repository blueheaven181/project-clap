"""Resolve immutable app resources and private mutable CLAP data."""

import os
import sys
from pathlib import Path


IS_FROZEN = bool(getattr(sys, "frozen", False))
SOURCE_ROOT = Path(__file__).resolve().parent.parent
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", SOURCE_ROOT)).resolve()

_local_app_data = os.environ.get("LOCALAPPDATA")
if not _local_app_data:
    _local_app_data = str(Path.home() / "AppData" / "Local")
PACKAGED_DATA_ROOT = Path(
    os.environ.get("CLAP_DATA_DIR", Path(_local_app_data) / "ProjectCLAP")
).resolve()

if IS_FROZEN:
    DATA_ROOT = PACKAGED_DATA_ROOT
else:
    DATA_ROOT = SOURCE_ROOT


def resource_path(*parts):
    """Return a read-only public resource path."""

    return RESOURCE_ROOT.joinpath(*parts)


def data_path(*parts):
    """Return a user-local mutable/private data path."""

    return DATA_ROOT.joinpath(*parts)


def ensure_data_parent(path):
    """Create the parent folder for one mutable user-local path."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
