"""Tests for GUI strings module — no Flet dependency."""

from __future__ import annotations

from motorsport_calendar.gui.strings import STRINGS, Strings, plural


class TestStrings:
    def test_app_title(self) -> None:
        assert STRINGS.app_title == "Motorsport Calendar"

    def test_generate_btn_is_user_friendly(self) -> None:
        assert "Générer" not in STRINGS.generate_btn
        assert "calendrier" in STRINGS.generate_btn.lower()

    def test_all_required_keys_present(self) -> None:
        required = [
            "app_title",
            "app_subtitle",
            "season_label",
            "championships_label",
            "output_label",
            "output_hint",
            "browse_tooltip",
            "save_dialog_title",
            "generate_btn",
            "generating_status",
            "success_title",
            "success_saved_at",
            "open_folder_btn",
            "close_btn",
            "error_no_events",
            "error_unexpected",
            "summary_ok",
            "summary_error",
        ]
        for key in required:
            assert hasattr(STRINGS, key), f"Missing string key: {key}"

    def test_summary_ok_format(self) -> None:
        result = STRINGS.summary_ok.format(name="Formula 1", n=24, s="s")
        assert "Formula 1" in result
        assert "24" in result

    def test_summary_error_format(self) -> None:
        result = STRINGS.summary_error.format(name="FIA WEC", err="source non implémentée")
        assert "FIA WEC" in result
        assert "non implémentée" in result

    def test_error_unexpected_format(self) -> None:
        result = STRINGS.error_unexpected.format(msg="connexion refusée")
        assert "connexion refusée" in result

    def test_from_dict_overrides_key(self) -> None:
        s = Strings.from_dict({"app_title": "Custom App"})
        assert s.app_title == "Custom App"

    def test_from_dict_original_unchanged(self) -> None:
        Strings.from_dict({"app_title": "Custom App"})
        assert STRINGS.app_title == "Motorsport Calendar"

    def test_from_dict_unknown_key_ignored(self) -> None:
        s = Strings.from_dict({"_nonexistent_xyz_key": "value"})
        assert not hasattr(s, "_nonexistent_xyz_key")

    def test_from_dict_partial_override(self) -> None:
        s = Strings.from_dict({"close_btn": "OK"})
        assert s.close_btn == "OK"
        assert s.app_title == "Motorsport Calendar"


class TestPlural:
    def test_zero_returns_s(self) -> None:
        assert plural(0) == "s"

    def test_one_returns_empty(self) -> None:
        assert plural(1) == ""

    def test_two_returns_s(self) -> None:
        assert plural(2) == "s"

    def test_negative_returns_s(self) -> None:
        assert plural(-1) == "s"
