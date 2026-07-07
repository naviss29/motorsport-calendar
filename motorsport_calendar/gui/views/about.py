"""ℹ À propos — about screen view.

Extracted from main_view.py so each view stays in its own module.
Requires url_launcher to open the GitHub link.

Sprint 28: compacted — the app name + version serve as the page's own
heading (no separate generic "À propos" label above them). Sprint 31: now
composed via the Layout System's ``PageContainer`` (no ``header=`` — this
page deliberately keeps its compact branding block as content rather than
the standard ``PageHeader``, unchanged from Sprint 28) + ``Section`` for
its content, instead of building its own container/spacing directly.
"""
from __future__ import annotations

import subprocess
import sys

import flet as ft

from motorsport_calendar.gui import theme
from motorsport_calendar.gui.components.layout import PageContainer, Section
from motorsport_calendar.gui.strings import STRINGS

_GITHUB_URL = "https://github.com/naviss29/motorsport-calendar"


def build_about_view(url_launcher: ft.UrlLauncher) -> ft.Control:
    """Return the À propos view, through the Layout System.

    Args:
        url_launcher: Flet UrlLauncher service registered in page.services.
    """

    async def on_github_click(e: ft.ControlEvent) -> None:
        try:
            await url_launcher.launch_url(_GITHUB_URL)
        except Exception:  # noqa: BLE001
            if sys.platform == "win32":
                subprocess.Popen(f"start {_GITHUB_URL}", shell=True)  # noqa: S602,S607

    branding_row = ft.Row(
        [
            theme.logo_placeholder("icon", size=theme.IconSize.XL),
            ft.Column(
                [
                    ft.Text(
                        STRINGS.app_title,
                        size=theme.FontSize.TITLE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        STRINGS.about_version,
                        size=theme.FontSize.SMALL,
                        color=theme.Colors.TEXT_MUTED,
                    ),
                ],
                spacing=2,
            ),
        ],
        spacing=theme.Spacing.SM,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    description = ft.Text(
        STRINGS.about_description,
        size=theme.FontSize.BODY,
        color=theme.Colors.TEXT_SECONDARY,
    )

    developer = ft.Text(
        STRINGS.about_developer,
        size=theme.FontSize.LABEL,
        weight=ft.FontWeight.W_500,
    )

    github_row = ft.Row(
        [
            ft.TextButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.OPEN_IN_NEW, size=theme.IconSize.SM),
                        ft.Text(STRINGS.about_github_label, size=theme.FontSize.BODY),
                    ],
                    spacing=theme.Spacing.XXS,
                    tight=True,
                ),
                on_click=on_github_click,
            )
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    license_text = ft.Text(
        STRINGS.about_license,
        size=theme.FontSize.SMALL,
        color=theme.Colors.TEXT_GHOST,
    )

    return PageContainer(
        body=[Section(branding_row, description, developer, github_row, license_text)],
    )
