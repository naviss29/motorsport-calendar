"""🏁 Ce week-end — version fonctionnelle (Sprint 29), Layout System (Sprint 31).

Renders one of exactly 3 states, driven by main_view.py:
  - loading  : ``build_weekend_view(None)``            — "Chargement..."
  - empty    : ``build_weekend_view(WeekendResult(found=False, ...))``
  - found    : ``build_weekend_view(WeekendResult(found=True, ...))``

Pure layout — fetching and finding the next race weekend lives in
``controller.get_upcoming_weekend`` / ``upcoming_weekend.py``. Every state
is composed from the Layout System (``PageContainer``/``PageHeader``/
``Section``/``CardList``/``EmptyState``) — this view builds no container,
padding, header, or card layout of its own.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from motorsport_calendar.gui import theme
from motorsport_calendar.gui.components.championship_card import build_championship_card
from motorsport_calendar.gui.components.layout import (
    CardList,
    EmptyState,
    PageContainer,
    PageHeader,
    Section,
)
from motorsport_calendar.gui.strings import STRINGS

if TYPE_CHECKING:
    from motorsport_calendar.gui.upcoming_weekend import WeekendResult

_HEADER_ICON = ft.Icons.SPORTS_MOTORSPORTS


def _loading_state() -> ft.Control:
    loading_card = theme.card(
        ft.Row(
            [
                ft.ProgressRing(width=16, height=16),
                ft.Text(
                    STRINGS.weekend_loading,
                    size=theme.FontSize.BODY,
                    color=theme.Colors.TEXT_SECONDARY,
                ),
            ],
            spacing=theme.Spacing.SM,
        )
    )
    return PageContainer(
        header=PageHeader(STRINGS.nav_weekend, icon=_HEADER_ICON),
        body=[Section(loading_card)],
    )


def _empty_state(result: WeekendResult) -> ft.Control:
    message = None
    if result.next_hint_date is not None:
        message = STRINGS.weekend_next_hint.format(date=f"{result.next_hint_date:%d/%m}")
    return PageContainer(
        header=PageHeader(STRINGS.nav_weekend, icon=_HEADER_ICON),
        body=[Section(EmptyState(STRINGS.weekend_empty_title, message=message))],
    )


def _found_state(result: WeekendResult) -> ft.Control:
    subtitle = f"{result.friday:%d/%m} - {result.sunday:%d/%m}"
    cards = [build_championship_card(card) for card in result.cards]
    return PageContainer(
        header=PageHeader(STRINGS.nav_weekend, icon=_HEADER_ICON, subtitle=subtitle),
        body=[Section(CardList(cards))],
    )


def build_weekend_view(result: WeekendResult | None = None) -> ft.Control:
    """Return the Ce week-end view for exactly one of the 3 states.

    Args:
        result: ``None`` while the fetch is in flight (loading state),
            otherwise the outcome of ``controller.get_upcoming_weekend``.
    """
    if result is None:
        return _loading_state()
    if not result.found:
        return _empty_state(result)
    return _found_state(result)
