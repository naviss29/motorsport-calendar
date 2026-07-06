"""⚙ Préférences — placeholder view.

Displays the full preference structure without any active controls.
Each row is a preview of a future setting backed by PreferencesModel.
"""
from __future__ import annotations

import flet as ft

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


def _coming_soon_chip() -> ft.Control:
    return ft.Container(
        content=ft.Text(
            STRINGS.prefs_coming_soon,
            size=11,
            color=ft.Colors.WHITE38,
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        border_radius=12,
        border=ft.Border.all(1, ft.Colors.WHITE12),
    )


def _pref_row(icon: ft.IconData, label: str) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, size=20, color=ft.Colors.WHITE54),
                ft.Text(label, size=13, color=ft.Colors.WHITE70, expand=True),
                _coming_soon_chip(),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        border_radius=8,
        border=ft.Border.all(1, ft.Colors.WHITE12),
    )


def build_preferences_view(model: PreferencesModel | None = None) -> ft.Control:
    """Return the Préférences placeholder view.

    Args:
        model: current preferences (unused for now — displayed when settings become active).
    """
    _ = model  # reserved for future binding

    rows = [_pref_row(icon, label) for icon, label, _ in _PREF_ROWS]

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SETTINGS, size=24, color=ft.Colors.WHITE70),
                        ft.Text(
                            STRINGS.prefs_title,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=16),
                ft.Column(controls=rows, spacing=8),
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=ft.Padding.symmetric(vertical=24, horizontal=28),
    )
