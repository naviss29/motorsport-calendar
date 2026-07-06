"""Tests for GUI preferences module — no Flet dependency."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from motorsport_calendar.gui.preferences import load_preferences, save_preferences


class TestLoadPreferences:
    def test_returns_defaults_on_first_run(self, tmp_path: Path) -> None:
        fake_file = tmp_path / "nonexistent" / "prefs.json"
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", fake_file):
            prefs = load_preferences()
        assert prefs["selected_championships"] == ["formula1"]

    def test_returns_saved_values(self, tmp_path: Path) -> None:
        prefs_file = tmp_path / "gui_prefs.json"
        prefs_file.write_text(
            json.dumps({"selected_championships": ["formula2", "formula3"]}),
            encoding="utf-8",
        )
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", prefs_file):
            prefs = load_preferences()
        assert prefs["selected_championships"] == ["formula2", "formula3"]

    def test_merges_with_defaults_for_new_keys(self, tmp_path: Path) -> None:
        prefs_file = tmp_path / "gui_prefs.json"
        prefs_file.write_text(
            json.dumps({"selected_championships": ["formula1"]}),
            encoding="utf-8",
        )
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", prefs_file):
            prefs = load_preferences()
        assert "last_output_dir" in prefs

    def test_handles_corrupted_json(self, tmp_path: Path) -> None:
        prefs_file = tmp_path / "gui_prefs.json"
        prefs_file.write_text("NOT_JSON {{{{", encoding="utf-8")
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", prefs_file):
            prefs = load_preferences()
        assert prefs["selected_championships"] == ["formula1"]

    def test_returns_dict(self, tmp_path: Path) -> None:
        fake_file = tmp_path / "prefs.json"
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", fake_file):
            prefs = load_preferences()
        assert isinstance(prefs, dict)


class TestSavePreferences:
    def test_roundtrip(self, tmp_path: Path) -> None:
        prefs_file = tmp_path / "sub" / "gui_prefs.json"
        data = {"selected_championships": ["formula3"], "last_output_dir": ""}
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", prefs_file):
            save_preferences(data)
            loaded = load_preferences()
        assert loaded["selected_championships"] == ["formula3"]

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        deep = tmp_path / "a" / "b" / "c" / "prefs.json"
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", deep):
            save_preferences({"selected_championships": ["formula1"], "last_output_dir": ""})
        assert deep.exists()

    def test_file_content_is_valid_json(self, tmp_path: Path) -> None:
        prefs_file = tmp_path / "gui_prefs.json"
        data = {"selected_championships": ["formula2"], "last_output_dir": "/tmp"}
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", prefs_file):
            save_preferences(data)
        content = prefs_file.read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert parsed["selected_championships"] == ["formula2"]

    def test_os_error_is_swallowed(self) -> None:
        mock_path = MagicMock(spec=Path)
        mock_path.parent.mkdir = MagicMock()
        mock_path.write_text = MagicMock(side_effect=OSError("disk full"))
        with patch("motorsport_calendar.gui.preferences._PREFS_FILE", mock_path):
            save_preferences({"selected_championships": []})  # must not raise
