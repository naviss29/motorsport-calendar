"""⭐ Mes favoris — placeholder view.

Future feature: quick access to user-pinned championships.
"""
from __future__ import annotations

import flet as ft

from motorsport_calendar.gui.strings import STRINGS


def build_favorites_view() -> ft.Control:
    """Return the Mes favoris placeholder view."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [ft.Icon(ft.Icons.STAR_BORDER, size=48, color=ft.Colors.AMBER_400)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(
                    STRINGS.nav_favorites,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.WHITE70,
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Text(
                        STRINGS.favorites_empty,
                        size=14,
                        color=ft.Colors.WHITE54,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=400,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(height=4),
                ft.Text(
                    STRINGS.favorites_coming_soon,
                    size=12,
                    color=ft.Colors.WHITE30,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        expand=True,
        padding=ft.Padding.all(32),
        alignment=ft.Alignment.TOP_CENTER,
    )
