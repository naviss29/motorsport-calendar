"""Persistence of GUI user preferences between sessions.

Stored at: ~/.config/motorsport-calendar/gui_prefs.json

Schema (all keys optional — missing keys fall back to _DEFAULTS):
  selected_championships: list[str]   IDs of checked championships
  last_output_dir:        str         Last directory used for saving the .ics
"""
from __future__ import annotations

import json
from pathlib import Path

_PREFS_FILE: Path = (
    Path.home() / ".config" / "motorsport-calendar" / "gui_prefs.json"
)

_DEFAULTS: dict = {
    "selected_championships": ["formula1"],
    "last_output_dir": "",
}


def load_preferences() -> dict:
    """Return saved preferences merged over defaults.

    On first run (no file) or corrupted JSON, returns a copy of _DEFAULTS.
    """
    try:
        data = json.loads(_PREFS_FILE.read_text(encoding="utf-8"))
        return {**_DEFAULTS, **data}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save_preferences(prefs: dict) -> None:
    """Persist preferences to disk. Silently swallows I/O errors."""
    try:
        _PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _PREFS_FILE.write_text(
            json.dumps(prefs, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        pass
