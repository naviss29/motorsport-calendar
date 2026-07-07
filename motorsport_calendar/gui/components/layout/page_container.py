"""PageContainer — the single page shell every view renders through.

Owns exactly one responsibility: max width, horizontal/vertical padding,
and overall alignment. A view never builds its own Container/padding/width
again — it hands PageContainer a header and a body, nothing more.

Internally this is ``theme.page_shell`` wearing a header/body-shaped API
instead of a flat ``*sections`` list, so every call site reads
declaratively instead of repeating the same Container/Column boilerplate:

    return PageContainer(
        header=PageHeader("Ce week-end", icon=ft.Icons.SPORTS_MOTORSPORTS),
        body=[Section(CardList(cards))],
    )

No new Design System tokens: this module only calls into ``theme.py``,
never redefines spacing/color/width values of its own.
"""
from __future__ import annotations

from collections.abc import Sequence

import flet as ft

from motorsport_calendar.gui import theme


def PageContainer(
    *,
    header: ft.Control | None = None,
    body: Sequence[ft.Control] = (),
) -> ft.Control:
    """Return the full page shell: header (if any) followed by the body.

    Args:
        header: the page's ``PageHeader``, or ``None`` for the rare page
            that renders its own title inline instead of the standard
            header (e.g. À propos's compact branding block).
        body: the page's content — already composed from ``Section``,
            ``CardList``, ``EmptyState``, or plain controls. Passed
            through untouched; this function adds no spacing logic of its
            own beyond what ``theme.page_shell`` already provides between
            top-level blocks.
    """
    sections: list[ft.Control] = []
    if header is not None:
        sections.append(header)
    sections.extend(body)
    return theme.page_shell(*sections)
