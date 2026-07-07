"""⚙ Préférences — placeholder view.

Displays the full preference structure without any active controls.
Each row is a preview of a future setting backed by PreferencesModel.

Sprint 31: composed from the Layout System — ``PageContainer``/``PageHeader``
put the page's own title above the content again (rather than absorbed
into a single card, per Sprint 28), and the rows are a ``CardList``: each
row is its own small bordered card, which no longer risks a double border
now that there is no single outer card wrapping the whole list.
"""
from __future__ import annotations

import flet as ft

from motorsport_calendar.gui import theme
from motorsport_calendar.gui.components.layout import CardList, PageContainer, PageHeader, Section
from motorsport_calendar.gui.models import PreferencesModel
from motorsport_calendar.gui.strings import STRINGS

# Ordered preference rows: (icon, label, field_name_in_PreferencesModel)
_PREF_ROWS: list[tuple[ft.IconData, str, str]] = [
    (ft.Icons.LANGUAGE,           STRINGS.prefs_language,           "language"),
    (ft.Icons.SCHEDULE,           STRINGS.prefs_timezone,           "timezone"),
    (ft.Icons.CALENDAR_TODAY,     STRINGS.prefs_first_day,          "first_day_of_week"),
    (ft.Icons.STAR_OUTLINE,       STRINGS.prefs_favorites,          "favorite_championships"),
    (ft.Icons.CALENDAR_MONTH,     STRINGS.prefs_preferred_calendar, "preferred_calendar"),
    (ft.Icons.CLOUD_SYNC_OUTLINED, STRINGS.prefs_bapps_sync,        "bapps_sync_enabled"),
]


def _pref_row(icon: ft.IconData, label: str) -> ft.Control:
    return theme.card(
        ft.Row(
            controls=[
                ft.Icon(icon, size=theme.IconSize.MD, color=theme.Colors.TEXT_MUTED),
                ft.Text(
                    label,
                    size=theme.FontSize.BODY,
                    color=theme.Colors.TEXT_SECONDARY,
                    expand=True,
                ),
                theme.chip(STRINGS.prefs_coming_soon),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.Spacing.SM,
        )
    )


def build_preferences_view(model: PreferencesModel | None = None) -> ft.Control:
    """Return the Préférences placeholder view, through the Layout System.

    Args:
        model: current preferences (unused for now — displayed when settings become active).
    """
    _ = model  # reserved for future binding

    rows = [_pref_row(icon, label) for icon, label, _ in _PREF_ROWS]

    return PageContainer(
        header=PageHeader(STRINGS.prefs_title, icon=ft.Icons.SETTINGS),
        body=[Section(CardList(rows))],
    )
