"""📅 Mon calendrier — ICS generation form view.

Receives pre-built controls from main_view.py (which owns state + handlers).
This module is responsible for layout only.
"""
from __future__ import annotations

from dataclasses import dataclass

import flet as ft

from motorsport_calendar.gui.strings import STRINGS


@dataclass
class CalendarViewControls:
    """Pre-built Flet controls injected from main_view.py.

    Separating layout (here) from state/handlers (main_view.py) keeps this
    module stateless and independently testable.
    """

    year_dropdown: ft.Dropdown
    championship_groups: list[ft.Control]
    output_field: ft.TextField
    browse_btn: ft.IconButton
    generate_btn: ft.Button
    progress_ring: ft.ProgressRing
    error_text: ft.Text


def build_calendar_view(c: CalendarViewControls) -> ft.Control:
    """Return the Mon calendrier form as a scrollable Container."""
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=24, color=ft.Colors.RED_400),
                        ft.Text(
                            STRINGS.app_title,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=16),

                # Saison
                ft.Text(STRINGS.season_label, size=13, weight=ft.FontWeight.W_500),
                c.year_dropdown,
                ft.Divider(height=10),

                # Championnats (groupés — fournis par main_view)
                ft.Text(STRINGS.championships_label, size=13, weight=ft.FontWeight.W_500),
                ft.Column(controls=c.championship_groups, spacing=2),
                ft.Divider(height=10),

                # Fichier de sortie
                ft.Text(STRINGS.output_label, size=13, weight=ft.FontWeight.W_500),
                ft.Row(
                    [c.output_field, c.browse_btn],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=16),

                # Action
                ft.Row(
                    [c.generate_btn, c.progress_ring],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                ),
                ft.Divider(height=6),
                c.error_text,
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=ft.Padding.symmetric(vertical=24, horizontal=28),
    )
