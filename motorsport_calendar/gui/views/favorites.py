"""⭐ Mes favoris — placeholder view.

Future feature: quick access to user-pinned championships.

Sprint 31: composed entirely from the Layout System (``PageContainer`` +
``PageHeader`` + ``Section`` + ``EmptyState``) — no page container, header,
or card wrapping built here directly.
"""
from __future__ import annotations

import flet as ft

from motorsport_calendar.gui.components.layout import EmptyState, PageContainer, PageHeader, Section
from motorsport_calendar.gui.strings import STRINGS


def build_favorites_view() -> ft.Control:
    """Return the Mes favoris placeholder view, through the Layout System."""
    return PageContainer(
        header=PageHeader(STRINGS.nav_favorites, icon=ft.Icons.STAR_BORDER),
        body=[Section(EmptyState(STRINGS.favorites_empty, message=STRINGS.favorites_coming_soon))],
    )
