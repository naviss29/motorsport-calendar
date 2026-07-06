"""ℹ À propos — about screen view.

Extracted from main_view.py so each view stays in its own module.
Requires url_launcher to open the GitHub link.
"""
from __future__ import annotations

import subprocess
import sys

import flet as ft

from motorsport_calendar.gui.strings import STRINGS

_GITHUB_URL = "https://github.com/naviss29/motorsport-calendar"


def build_about_view(url_launcher: ft.UrlLauncher) -> ft.Control:
    """Return the À propos view.

    Args:
        url_launcher: Flet UrlLauncher service registered in page.services.
    """

    async def on_github_click(e: ft.ControlEvent) -> None:
        try:
            await url_launcher.launch_url(_GITHUB_URL)
        except Exception:  # noqa: BLE001
            if sys.platform == "win32":
                subprocess.Popen(f"start {_GITHUB_URL}", shell=True)  # noqa: S602,S607

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=48, color=ft.Colors.RED_400)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(
                    STRINGS.app_title,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    STRINGS.about_version,
                    size=13,
                    color=ft.Colors.WHITE54,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=16),
                ft.Divider(),
                ft.Container(height=8),
                ft.Text(
                    STRINGS.about_description,
                    size=13,
                    color=ft.Colors.WHITE70,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=16),
                ft.Text(
                    STRINGS.about_developer,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Row(
                    [
                        ft.TextButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.OPEN_IN_NEW, size=14),
                                    ft.Text(STRINGS.about_github_label, size=13),
                                ],
                                spacing=4,
                                tight=True,
                            ),
                            on_click=on_github_click,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=8),
                ft.Text(
                    STRINGS.about_license,
                    size=12,
                    color=ft.Colors.WHITE38,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        ),
        expand=True,
        padding=ft.Padding.all(32),
        alignment=ft.Alignment.TOP_CENTER,
    )
