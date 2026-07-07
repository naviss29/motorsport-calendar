"""Smoke tests for GUI view builders.

Verify that each view module is importable and its builder returns a Flet control.
No Flet runtime required — controls are dataclasses and instantiate without a page.
"""

from __future__ import annotations

import flet as ft

from motorsport_calendar.gui import theme
from motorsport_calendar.gui.models import PreferencesModel


def _bordered_cards(control: ft.Control) -> list[ft.Container]:
    """Recursively collect every bordered Container under *control* — used
    to assert "N cards present" without hardcoding exact nesting depth
    (Section/CardList/PageHeader each add their own wrapping Column)."""
    found: list[ft.Container] = []
    if isinstance(control, ft.Container) and control.border is not None:
        found.append(control)
    for attr in ("controls", "content"):
        child = getattr(control, attr, None)
        if isinstance(child, list):
            for c in child:
                found.extend(_bordered_cards(c))
        elif isinstance(child, ft.Control):
            found.extend(_bordered_cards(child))
    return found


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

    def test_uses_shared_page_shell(self):
        from motorsport_calendar.gui.views.weekend import build_weekend_view
        view = build_weekend_view()
        assert view.content.width == theme.MAX_CONTENT_WIDTH

    def test_content_lives_inside_a_central_card(self):
        """Sprint 28: an empty placeholder page must not read as broken —
        its content sits inside one bordered central card, not loose.
        (default arg = loading state, still card-wrapped.) Sprint 31: the
        page header is now a separate PageHeader above the card, not
        absorbed into it — so we look for the card anywhere in the tree
        rather than assuming it's the only top-level section."""
        from motorsport_calendar.gui.views.weekend import build_weekend_view
        view = build_weekend_view()
        assert len(_bordered_cards(view)) == 1

    def test_loading_state_is_card_wrapped(self):
        """Sprint 29: `result=None` means the background fetch hasn't
        resolved yet."""
        from motorsport_calendar.gui.views.weekend import build_weekend_view
        view = build_weekend_view(None)
        assert len(_bordered_cards(view)) == 1

    def test_empty_state_is_card_wrapped_with_hint(self):
        from datetime import date

        from motorsport_calendar.gui.upcoming_weekend import WeekendResult
        from motorsport_calendar.gui.views.weekend import build_weekend_view

        result = WeekendResult(found=False, next_hint_date=date(2026, 8, 14))
        view = build_weekend_view(result)
        assert len(_bordered_cards(view)) == 1

    def test_page_header_is_present_above_the_content(self):
        """Sprint 31: every "Ce week-end" state shows its own PageHeader —
        no longer absorbed into the card, for consistency with every
        other page in the app."""
        from motorsport_calendar.gui.views.weekend import build_weekend_view
        view = build_weekend_view()
        column = view.content.content
        assert len(column.controls) == 2  # PageHeader, then the body

    def test_empty_state_without_hint_does_not_crash(self):
        from motorsport_calendar.gui.upcoming_weekend import WeekendResult
        from motorsport_calendar.gui.views.weekend import build_weekend_view

        result = WeekendResult(found=False, next_hint_date=None)
        view = build_weekend_view(result)
        assert isinstance(view, ft.Control)

    def test_found_state_renders_one_card_per_championship(self):
        from datetime import date

        from motorsport_calendar.gui.components.championship_card import (
            ChampionshipCardData,
            SessionRow,
        )
        from motorsport_calendar.gui.upcoming_weekend import WeekendResult
        from motorsport_calendar.gui.views.weekend import build_weekend_view

        result = WeekendResult(
            found=True,
            friday=date(2026, 7, 10),
            sunday=date(2026, 7, 12),
            cards=(
                ChampionshipCardData(
                    championship_id="formula1",
                    championship_name="Formula 1",
                    event_name="Grand Prix du Japon",
                    circuit_name="Suzuka",
                    country="🇯🇵 Japon",
                    sessions=(SessionRow("Course", "Dimanche 14:00"),),
                ),
                ChampionshipCardData(
                    championship_id="wec",
                    championship_name="FIA WEC",
                    event_name="6 Hours of Spa",
                    circuit_name="Spa",
                    country="🇧🇪 Belgique",
                    sessions=(SessionRow("Course", "Samedi 15:00"),),
                ),
            ),
        )
        view = build_weekend_view(result)
        assert len(_bordered_cards(view)) == 2

    def test_found_state_with_no_cards_does_not_crash(self):
        """Defensive: found=True with an empty cards tuple must still render."""
        from datetime import date

        from motorsport_calendar.gui.upcoming_weekend import WeekendResult
        from motorsport_calendar.gui.views.weekend import build_weekend_view

        result = WeekendResult(found=True, friday=date(2026, 7, 10), sunday=date(2026, 7, 12))
        view = build_weekend_view(result)
        assert isinstance(view, ft.Control)


class TestCalendarView:
    def _make_controls(self, **overrides):
        from motorsport_calendar.gui.views.calendar import CalendarViewControls
        defaults = {
            "year_dropdown": ft.Dropdown(label="Saison", value="2026"),
            "output_field": ft.TextField(label="Fichier"),
            "browse_btn": ft.IconButton(icon=ft.Icons.FOLDER_OPEN),
            "generate_btn": ft.Button(content="Créer"),
            "progress_ring": ft.ProgressRing(width=22, height=22, visible=False),
            "error_text": ft.Text(value=""),
            "back_btn": ft.Button(content="Précédent"),
            "next_btn": ft.Button(content="Suivant"),
            "championship_groups": [ft.Checkbox(label="Formula 1", value=True)],
            "recap_controls": [ft.Text("2026"), ft.Text("Formula 1"), ft.Text("out.ics")],
        }
        defaults.update(overrides)
        return CalendarViewControls(**defaults)

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

    def test_uses_shared_page_shell(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        view = build_calendar_view(self._make_controls())
        assert view.content.width == theme.MAX_CONTENT_WIDTH

    def test_calendar_view_controls_dataclass(self):
        from motorsport_calendar.gui.views.calendar import CalendarViewControls
        c = self._make_controls()
        assert isinstance(c, CalendarViewControls)
        assert isinstance(c.year_dropdown, ft.Dropdown)
        assert isinstance(c.championship_groups, list)

    def test_default_step_is_zero(self):
        c = self._make_controls()
        assert c.current_step == 0

    def test_step_body_has_no_redundant_title(self):
        """Sprint 28: the step indicator (pastilles) is enough — each step's
        content starts directly with its field, no "Étape N — ..." title +
        help text above it anymore."""
        from motorsport_calendar.gui.views.calendar import _step_season
        c = self._make_controls()
        body = _step_season(c)
        assert isinstance(body, ft.Column)
        assert body.controls == [c.year_dropdown]

    def test_default_on_step_click_is_noop(self):
        c = self._make_controls()
        c.on_step_click(2)  # must not raise

    def test_build_every_step_returns_control(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        for step in range(4):
            view = build_calendar_view(self._make_controls(current_step=step))
            assert isinstance(view, ft.Control)

    def test_step_zero_hides_back_button(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        c = self._make_controls(current_step=0)
        build_calendar_view(c)
        assert c.back_btn.visible is False
        assert c.next_btn.visible is True

    def test_last_step_hides_next_button(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        c = self._make_controls(current_step=3)
        build_calendar_view(c)
        assert c.next_btn.visible is False
        assert c.back_btn.visible is True

    def test_middle_step_shows_both_nav_buttons(self):
        from motorsport_calendar.gui.views.calendar import build_calendar_view
        c = self._make_controls(current_step=1)
        build_calendar_view(c)
        assert c.back_btn.visible is True
        assert c.next_btn.visible is True

    def test_step_indicator_click_calls_callback(self):
        from motorsport_calendar.gui.views.calendar import STEP_LABELS
        assert len(STEP_LABELS) == 4
        clicked: list[int] = []
        c = self._make_controls(current_step=2, on_step_click=clicked.append)
        from motorsport_calendar.gui.views.calendar import _step_indicator
        indicator = _step_indicator(c)
        assert isinstance(indicator, ft.Control)


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

    def test_uses_shared_page_shell(self):
        from motorsport_calendar.gui.views.favorites import build_favorites_view
        view = build_favorites_view()
        assert view.content.width == theme.MAX_CONTENT_WIDTH

    def test_content_lives_inside_a_central_card(self):
        """Sprint 28: an empty placeholder page must not read as broken —
        its content sits inside one bordered central card, not loose.
        Sprint 31: the page header is now separate (PageHeader), so we
        look for the card anywhere in the tree rather than assuming it's
        the only top-level section."""
        from motorsport_calendar.gui.views.favorites import build_favorites_view
        view = build_favorites_view()
        assert len(_bordered_cards(view)) == 1

    def test_page_header_is_present_above_the_empty_state(self):
        from motorsport_calendar.gui.views.favorites import build_favorites_view
        view = build_favorites_view()
        column = view.content.content
        assert len(column.controls) == 2  # PageHeader, then the body


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

    def test_uses_shared_page_shell(self):
        from motorsport_calendar.gui.views.preferences import build_preferences_view
        view = build_preferences_view()
        assert view.content.width == theme.MAX_CONTENT_WIDTH

    def test_rows_render_as_a_card_list(self):
        """Sprint 31: each row is its own small CardList card — no more
        single outer card wrapping the whole list (see Sprint 28 vs. 31 in
        the journal for why the border came back). Each row also embeds a
        "coming soon" chip, which is itself a bordered container — so we
        count cards at exactly 2x the row count (row + its chip) rather
        than assuming every bordered container is a distinct card."""
        from motorsport_calendar.gui.views.preferences import _PREF_ROWS, build_preferences_view
        view = build_preferences_view()
        assert len(_bordered_cards(view)) == len(_PREF_ROWS) * 2

    def test_page_header_is_present_above_the_card_list(self):
        from motorsport_calendar.gui.views.preferences import build_preferences_view
        view = build_preferences_view()
        column = view.content.content
        assert len(column.controls) == 2  # PageHeader, then the body

    def test_pref_rows_now_carry_their_own_border(self):
        """Sprint 31: rows are no longer nested inside one big outer card
        (that card is gone — PageHeader is now separate from the body), so
        each row can safely be its own bordered card again, uniformly via
        CardList."""
        from motorsport_calendar.gui.views.preferences import _pref_row
        row = _pref_row(ft.Icons.LANGUAGE, "Langue")
        assert isinstance(row, ft.Container)
        assert row.border is not None


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

    def test_uses_shared_page_shell(self):
        from motorsport_calendar.gui.views.about import build_about_view
        view = build_about_view(ft.UrlLauncher())
        assert view.content.width == theme.MAX_CONTENT_WIDTH

    def test_content_is_not_wrapped_in_a_card(self):
        """Sprint 28 task 3 reorganizes À propos compactly — unlike the 3
        empty placeholder pages, it does not get a card wrapper."""
        from motorsport_calendar.gui.views.about import build_about_view
        view = build_about_view(ft.UrlLauncher())
        column = view.content.content
        for section in column.controls:
            assert not (isinstance(section, ft.Container) and section.border is not None)

    def test_app_title_and_version_shown_once(self):
        """The generic "À propos" label is gone — the app name/version
        block is now the page's own heading, shown exactly once."""
        from motorsport_calendar.gui.strings import STRINGS
        from motorsport_calendar.gui.views.about import build_about_view
        view = build_about_view(ft.UrlLauncher())

        def _collect_text(control, acc):
            if isinstance(control, ft.Text) and isinstance(control.value, str):
                acc.append(control.value)
            for attr in ("controls", "content"):
                child = getattr(control, attr, None)
                if isinstance(child, list):
                    for c in child:
                        _collect_text(c, acc)
                elif child is not None:
                    _collect_text(child, acc)
            return acc

        texts = _collect_text(view, [])
        assert texts.count(STRINGS.app_title) == 1


class TestAllViewsShareTheSameGrid:
    """Sprint 27 — every page must use the exact same layout grid."""

    def _all_views(self):
        from motorsport_calendar.gui.views.about import build_about_view
        from motorsport_calendar.gui.views.calendar import CalendarViewControls, build_calendar_view
        from motorsport_calendar.gui.views.favorites import build_favorites_view
        from motorsport_calendar.gui.views.preferences import build_preferences_view
        from motorsport_calendar.gui.views.weekend import build_weekend_view

        calendar_controls = CalendarViewControls(
            year_dropdown=ft.Dropdown(label="Saison", value="2026"),
            output_field=ft.TextField(label="Fichier"),
            browse_btn=ft.IconButton(icon=ft.Icons.FOLDER_OPEN),
            generate_btn=ft.Button(content="Créer"),
            progress_ring=ft.ProgressRing(width=22, height=22, visible=False),
            error_text=ft.Text(value=""),
            back_btn=ft.Button(content="Précédent"),
            next_btn=ft.Button(content="Suivant"),
        )
        return [
            build_weekend_view(),
            build_calendar_view(calendar_controls),
            build_favorites_view(),
            build_preferences_view(),
            build_about_view(ft.UrlLauncher()),
        ]

    def test_every_view_is_a_container_expanding_to_fill(self):
        for view in self._all_views():
            assert isinstance(view, ft.Container)
            assert view.expand is True

    def test_every_view_shares_the_same_max_content_width(self):
        widths = {view.content.width for view in self._all_views()}
        assert widths == {theme.MAX_CONTENT_WIDTH}

    def test_every_view_centers_horizontally_not_its_content(self):
        for view in self._all_views():
            assert view.alignment == ft.Alignment.TOP_CENTER

    def test_every_view_left_aligns_its_content_column(self):
        for view in self._all_views():
            column = view.content.content
            assert column.horizontal_alignment == ft.CrossAxisAlignment.STRETCH

    def test_every_view_uses_the_same_outer_padding(self):
        expected = theme.page_padding()
        for view in self._all_views():
            assert view.padding == expected
