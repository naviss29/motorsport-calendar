"""Smoke tests for GUI view builders.

Verify that each view module is importable and its builder returns a Flet control.
No Flet runtime required — controls are dataclasses and instantiate without a page.
"""

from __future__ import annotations

import flet as ft
import pytest

from motorsport_calendar.gui.models import PreferencesModel


class TestWeekendView:
    def test_import(self):
        from motorsport_calendar.gui.views import weekend  # noqa: F401

    def test_build_returns_control(self):
        from motorsport_calendar.gui.views.weekend import build_weekend_view
        view = build_weekend_view()
        assert isinstance(view, ft.Control)

    def test_build_is_container(self):
        from motorsport_calendar.gui.views.weekend import build_weekend_view
        view = build_weekend_view()
        assert isinstance(view, ft.Container)

    def test_expand_true(self):
        from motorsport_calendar.gui.views.weekend import build_weekend_view
        view = build_weekend_view()
        assert view.expand is True


class TestCalendarView:
    def _make_controls(self):
        from motorsport_calendar.gui.views.calendar import CalendarViewControls
        return CalendarViewControls(
            year_dropdown=ft.Dropdown(label="Saison", value="2026"),
            championship_groups=[ft.Checkbox(label="Formula 1", value=True)],
            output_field=ft.TextField(label="Fichier"),
            browse_btn=ft.IconButton(icon=ft.Icons.FOLDER_OPEN),
            generate_btn=ft.Button(content="Créer"),
            progress_ring=ft.ProgressRing(width=22, height=22, visible=False),
            error_text=ft.Text(value=""),
        )

    def test_import(self):
        from motorsport_calendar.gui.views import calendar  # noqa: F401

    def test_build_returns_control(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        view = build_calendar_view(self._make_controls())
        assert isinstance(view, ft.Control)

    def test_build_is_container(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        view = build_calendar_view(self._make_controls())
        assert isinstance(view, ft.Container)

    def test_expand_true(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        view = build_calendar_view(self._make_controls())
        assert view.expand is True

    def test_calendar_view_controls_dataclass(self):
        from motorsport_calendar.gui.views.calendar import CalendarViewControls
        c = self._make_controls()
        assert isinstance(c, CalendarViewControls)
        assert isinstance(c.year_dropdown, ft.Dropdown)
        assert isinstance(c.championship_groups, list)


class TestFavoritesView:
    def test_import(self):
        from motorsport_calendar.gui.views import favorites  # noqa: F401

    def test_build_returns_control(self):
        from motorsport_calendar.gui.views.favorites import build_favorites_view
        view = build_favorites_view()
        assert isinstance(view, ft.Control)

    def test_expand_true(self):
        from motorsport_calendar.gui.views.favorites import build_favorites_view
        view = build_favorites_view()
        assert view.expand is True


class TestPreferencesView:
    def test_import(self):
        from motorsport_calendar.gui.views import preferences  # noqa: F401

    def test_build_returns_control(self):
        from motorsport_calendar.gui.views.preferences import build_preferences_view
        view = build_preferences_view()
        assert isinstance(view, ft.Control)

    def test_build_with_model(self):
        from motorsport_calendar.gui.views.preferences import build_preferences_view
        model = PreferencesModel(language="en", timezone="America/New_York")
        view = build_preferences_view(model)
        assert isinstance(view, ft.Control)

    def test_build_without_model(self):
        from motorsport_calendar.gui.views.preferences import build_preferences_view
        view = build_preferences_view(None)
        assert isinstance(view, ft.Control)

    def test_expand_true(self):
        from motorsport_calendar.gui.views.preferences import build_preferences_view
        view = build_preferences_view()
        assert view.expand is True

    def test_pref_rows_count(self):
        from motorsport_calendar.gui.views.preferences import _PREF_ROWS
        assert len(_PREF_ROWS) == 6

    def test_pref_rows_structure(self):
        from motorsport_calendar.gui.views.preferences import _PREF_ROWS
        for icon, label, field_name in _PREF_ROWS:
            assert icon is not None
            assert isinstance(label, str)
            assert len(label) > 0
            assert hasattr(PreferencesModel, field_name) or hasattr(PreferencesModel(), field_name)


class TestAboutView:
    def test_import(self):
        from motorsport_calendar.gui.views import about  # noqa: F401

    def test_build_returns_control(self):
        from motorsport_calendar.gui.views.about import build_about_view
        launcher = ft.UrlLauncher()
        view = build_about_view(launcher)
        assert isinstance(view, ft.Control)

    def test_github_url_defined(self):
        from motorsport_calendar.gui.views.about import _GITHUB_URL
        assert _GITHUB_URL.startswith("https://github.com/")

    def test_expand_true(self):
        from motorsport_calendar.gui.views.about import build_about_view
        view = build_about_view(ft.UrlLauncher())
        assert view.expand is True
