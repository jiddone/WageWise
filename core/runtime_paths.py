"""Helper per risolvere path runtime in sviluppo e da eseguibile."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def get_base_path() -> Path:
    """Restituisce la root dell'app, compatibile con PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def get_data_path() -> Path:
    """Restituisce la cartella dati utente, specifica per OS."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / "WageWise" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_assets_path() -> Path:
    return get_base_path() / "assets"


def get_stylesheet_path() -> Path:
    return get_assets_path() / "style.qss"


def get_window_icon_path() -> Path:
    return get_assets_path() / "icon" / "favicon.ico"


def get_sidebar_logo_path() -> Path:
    return get_assets_path() / "icon" / "android-chrome-192x192.png"