"""🏁 Ce week-end — placeholder view.

Layout skeleton for the upcoming race-weekend overview feature.
No data fetching in this version — structure only.
"""
from __future__ import annotations

import flet as ft

from motorsport_calendar.gui.strings import STRINGS


def _placeholder_race_card() -> ft.Control:
    """Visual skeleton of a future race card (no live data)."""

    def _row(icon: ft.IconData, label: str) -> ft.Control:
        return ft.Row(
            [
                ft.Icon(icon, size=16, color=ft.Colors.WHITE38),
                ft.Text(label, size=13, color=ft.Colors.WHITE38, italic=True),
            ],
            spacing=8,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=18, color=ft.Colors.WHITE30),
                        ft.Text(
                            STRINGS.weekend_layout_preview,
                            size=12,
                            color=ft.Colors.WHITE30,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    spacing=6,
                ),
                ft.Divider(height=8, color=ft.Colors.WHITE12),
                _row(ft.Icons.EMOJI_EVENTS_OUTLINED, STRINGS.weekend_section_championship),
                _row(ft.Icons.STADIUM_OUTLINED, STRINGS.weekend_section_circuit),
                _row(ft.Icons.FLAG_OUTLINED, STRINGS.weekend_section_country),
                ft.Divider(height=8, color=ft.Colors.WHITE12),
                ft.Text(
                    STRINGS.weekend_section_sessions,
                    size=12,
                    color=ft.Colors.WHITE30,
                    weight=ft.FontWeight.W_500,
                ),
                _row(ft.Icons.SCHEDULE_OUTLINED, "— : —  ·  —"),
                _row(ft.Icons.SCHEDULE_OUTLINED, "— : —  ·  —"),
            ],
            spacing=6,
        ),
        padding=ft.Padding.all(16),
        border_radius=8,
        border=ft.Border.all(1, ft.Colors.WHITE12),
        width=320,
    )


def build_weekend_view() -> ft.Control:
    """Return the Ce week-end placeholder view."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=48, color=ft.Colors.WHITE30)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(
                    STRINGS.weekend_empty_title,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.WHITE70,
                ),
                ft.Text(
                    STRINGS.weekend_coming_soon,
                    size=13,
                    color=ft.Colors.WHITE38,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.Row(
                    [_placeholder_race_card()],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        expand=True,
        padding=ft.Padding.all(32),
        alignment=ft.Alignment.TOP_CENTER,
    )
