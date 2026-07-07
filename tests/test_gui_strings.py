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

    def test_wizard_step_labels_still_present(self) -> None:
        """Sprint 28: the pastilles' own labels must survive the cleanup."""
        for key in (
            "wizard_step_season",
            "wizard_step_championships",
            "wizard_step_destination",
            "wizard_step_create",
        ):
            assert hasattr(STRINGS, key)

    def test_redundant_wizard_step_titles_removed(self) -> None:
        """Sprint 28: "Étape N — ..." title + help text dropped — the step
        indicator (pastilles) is enough on its own, per-step body starts
        directly with its field.
        """
        for key in (
            "wizard_title_season",
            "wizard_help_season",
            "wizard_title_championships",
            "wizard_help_championships",
            "wizard_title_destination",
            "wizard_help_destination",
            "wizard_title_create",
            "wizard_help_create",
        ):
            assert not hasattr(STRINGS, key), f"stale wizard string still present: {key}"


class TestPlural:
    def test_zero_returns_s(self) -> None:
        assert plural(0) == "s"

    def test_one_returns_empty(self) -> None:
        assert plural(1) == ""

    def test_two_returns_s(self) -> None:
        assert plural(2) == "s"

    def test_negative_returns_s(self) -> None:
        assert plural(-1) == "s"
