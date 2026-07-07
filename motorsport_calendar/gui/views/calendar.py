"""📅 Mon calendrier — ICS generation wizard.

Sprint 26 (Release Alpha Phase 2) turned this from a single long form into
a guided 4-step wizard: saison → championnats → destination → créer.
Sprint 31: the page shell/header now come from the Layout System
(``PageContainer``/``PageHeader``/``PageSpacing``) — the wizard-specific
step indicator, step body, and nav row stay as plain controls in the body
list, since they are sequential wizard chrome, not a generic "section".

Receives pre-built controls from main_view.py (which owns state + handlers).
This module is responsible for layout only — it does not mutate state.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import flet as ft

from motorsport_calendar.gui import theme
from motorsport_calendar.gui.components.layout import PageContainer, PageHeader, PageSpacing
from motorsport_calendar.gui.strings import STRINGS

STEP_LABELS: tuple[str, ...] = (
    STRINGS.wizard_step_season,
    STRINGS.wizard_step_championships,
    STRINGS.wizard_step_destination,
    STRINGS.wizard_step_create,
)


@dataclass
class CalendarViewControls:
    """Pre-built Flet controls + wizard position injected from main_view.py.

    Separating layout (here) from state/handlers (main_view.py) keeps this
    module stateless and independently testable.
    """

    # Step 1 — Saison
    year_dropdown: ft.Dropdown

    # Step 3 — Destination
    output_field: ft.TextField
    browse_btn: ft.IconButton

    # Step 4 — Créer
    generate_btn: ft.Button
    progress_ring: ft.ProgressRing
    error_text: ft.Text

    # Navigation (always present — visibility toggled per step)
    back_btn: ft.Button
    next_btn: ft.Button

    # Step 2 — Championnats
    championship_groups: list[ft.Control] = field(default_factory=list)

    # Step 4 — Créer (recap rows built from current state)
    recap_controls: list[ft.Control] = field(default_factory=list)

    current_step: int = 0
    on_step_click: Callable[[int], None] = field(default=lambda step: None)


def _step_indicator(c: CalendarViewControls) -> ft.Control:
    """Row of 4 clickable step chips. Only completed/current steps are clickable."""
    chips: list[ft.Control] = []
    for i, label in enumerate(STEP_LABELS):
        is_current = i == c.current_step
        is_done = i < c.current_step
        is_reachable = i <= c.current_step

        if is_done:
            badge_color = theme.Colors.SUCCESS
            badge_content = ft.Icon(
                ft.Icons.CHECK, size=theme.IconSize.SM, color=theme.Colors.SUCCESS
            )
        else:
            badge_color = theme.Colors.PRIMARY if is_current else theme.Colors.TEXT_GHOST
            badge_content = ft.Text(
                str(i + 1),
                size=theme.FontSize.SMALL,
                color=badge_color,
                weight=ft.FontWeight.BOLD,
            )

        chip = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=badge_content,
                        width=24,
                        height=24,
                        border_radius=theme.Radius.PILL,
                        border=ft.Border.all(1.5, badge_color),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(
                        label,
                        size=theme.FontSize.SMALL,
                        color=theme.Colors.TEXT_PRIMARY if is_current else theme.Colors.TEXT_MUTED,
                        weight=ft.FontWeight.W_600 if is_current else ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=theme.Spacing.XXS,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=theme.Spacing.XS, vertical=theme.Spacing.XXS),
            border_radius=theme.Radius.PILL,
            on_click=(lambda e, step=i: c.on_step_click(step)) if is_reachable else None,
        )
        chips.append(chip)
        if i < len(STEP_LABELS) - 1:
            chips.append(ft.Container(width=16, height=1, bgcolor=theme.Colors.BORDER))

    return ft.Row(chips, spacing=theme.Spacing.XXS, wrap=True)


def _step_season(c: CalendarViewControls) -> ft.Control:
    """Step content starts right after the step indicator — Sprint 28 dropped
    the redundant "Étape N — ..." title + help text; the pastilles are enough.
    """
    return ft.Column([c.year_dropdown], spacing=theme.Spacing.SM)


def _step_championships(c: CalendarViewControls) -> ft.Control:
    return ft.Column(
        controls=c.championship_groups,
        spacing=2,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _step_destination(c: CalendarViewControls) -> ft.Control:
    return ft.Row(
        [c.output_field, c.browse_btn],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _step_create(c: CalendarViewControls) -> ft.Control:
    return ft.Column(
        [
            ft.Column(
                controls=c.recap_controls,
                spacing=theme.Spacing.XS,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            PageSpacing(theme.Spacing.MD),
            ft.Row(
                [c.generate_btn, c.progress_ring],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=theme.Spacing.SM,
            ),
            PageSpacing(theme.Spacing.XXS),
            c.error_text,
        ],
        spacing=theme.Spacing.SM,
    )


_STEP_BUILDERS: tuple[Callable[[CalendarViewControls], ft.Control], ...] = (
    _step_season,
    _step_championships,
    _step_destination,
    _step_create,
)


def build_calendar_view(c: CalendarViewControls) -> ft.Control:
    """Return the "Mon calendrier" wizard, through the Layout System.

    Renders exactly one of the 4 steps based on ``c.current_step``. Navigation
    (back/next) buttons are the same instances across steps — only their
    ``visible`` flag changes here, in pure layout code.
    """
    step_body = _STEP_BUILDERS[c.current_step](c)

    c.back_btn.visible = c.current_step > 0
    c.next_btn.visible = c.current_step < len(STEP_LABELS) - 1

    nav_row = ft.Row(
        [c.back_btn, c.next_btn],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    return PageContainer(
        header=PageHeader(STRINGS.nav_my_calendar, icon=ft.Icons.CALENDAR_MONTH),
        body=[
            _step_indicator(c),
            ft.Divider(height=theme.Spacing.MD),
            ft.Container(content=step_body, expand=True),
            ft.Divider(height=theme.Spacing.SM),
            nav_row,
        ],
    )
