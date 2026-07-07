"""PageHeader — the one page-title component every view uses.

Bundles icon + title + optional subtitle + the trailing separator into a
single control, so no view builds its own ``theme.section_title() +
ft.Divider()`` pair again. Every page that shows a header uses exactly
this component — one visual identity for "this is the top of a page",
everywhere, today and in every future screen.
"""
from __future__ import annotations

import flet as ft

from motorsport_calendar.gui import theme


def PageHeader(
    title: str,
    *,
    icon: ft.IconData | None = None,
    subtitle: str | None = None,
) -> ft.Control:
    """Return the page header block: icon + title, optional subtitle, divider.

    Args:
        title: the page's own name (e.g. "Ce week-end", "Préférences") —
            typically the same label shown in the navigation rail.
        icon: optional leading icon, matching the page's nav destination.
        subtitle: optional secondary line under the title (e.g. a date
            range) — always plain, muted text; no further styling knobs.
    """
    rows: list[ft.Control] = [theme.section_title(title, icon=icon)]
    if subtitle is not None:
        rows.append(ft.Text(subtitle, size=theme.FontSize.SMALL, color=theme.Colors.TEXT_MUTED))
    rows.append(ft.Divider(height=theme.Spacing.MD))
    return ft.Column(rows, spacing=theme.Spacing.XXS)
