"""⚙ Préférences — real configuration center (Sprint 52).

Notifications/Mises à jour/Calendrier are real, persisted settings —
``NotificationService`` and the ``update_check_enabled``/``default_year``/
``ics_alarm_minutes`` preferences (Sprint 51/52, ``gui/preferences.py``).
The Application section (Thème/Langue/Format horaire) stays a "coming
soon" placeholder — the Sprint 52 brief asks these fields to be
*prepared* ("pensées pour évoluer"), not necessarily implemented (see
``gui/models.py::PreferencesModel``).

No business logic here: main_view.py owns ``NotificationService``/
``FavoritesService``/the raw preferences dict, and builds every Flet
control (switches/dropdowns) with its ``on_change`` handler already
wired — this module only arranges the pre-built controls into the Layout
System, same "view renders, main_view.py decides" split as every other
interactive page (see ``views/calendar.py``'s ``CalendarViewControls``).

Sprint 54 (Beta UX recette): the hint-line spacing in ``_control_row``
now uses ``theme.Spacing.XXS`` (4px) instead of a bare ``2`` — the
Design System's own smallest step, not a number outside its scale
(``theme.py``'s own rule: "no view should hardcode ... a raw padding
int"). 2px vs 4px is not a visible regression in a single-pixel-dense
label/hint pairing.

Sprint 57 (Préparation Beta — nettoyage): the local "coming soon" row
(``_pref_row``) is gone — promoted to ``gui/components/layout::
ComingSoonRow`` once "Soutenir le projet" needed the exact same shape
for its PayPal/GitHub Sponsors placeholders. This module now imports and
uses it, never redefines it — same "mutualize on the second real use"
principle as ``championship_selector.py``.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import flet as ft

from motorsport_calendar.gui import theme
from motorsport_calendar.gui.components.layout import (
    CardList,
    ComingSoonRow,
    PageContainer,
    PageHeader,
    Section,
    SectionHeader,
)
from motorsport_calendar.gui.models import PreferencesModel
from motorsport_calendar.gui.strings import STRINGS, plural

# "Application" section — prepared, not implemented (Sprint 52 brief):
# (icon, label, PreferencesModel field name).
_PREF_ROWS: list[tuple[ft.IconData, str, str]] = [
    (ft.Icons.DARK_MODE_OUTLINED, STRINGS.prefs_theme, "theme"),
    (ft.Icons.LANGUAGE, STRINGS.prefs_language, "language"),
    (ft.Icons.SCHEDULE, STRINGS.prefs_time_format, "time_format"),
]


@dataclass
class PreferencesViewControls:
    """Pre-built Flet controls (``on_change`` already wired by
    main_view.py) + pure display data injected from main_view.py, which
    owns state/handlers/service calls — this module only lays them out.
    """

    notifications_enabled_switch: ft.Switch
    notifications_favorites_only_switch: ft.Switch
    notifications_lead_time_dropdown: ft.Dropdown
    favorite_count: int

    update_check_enabled_switch: ft.Switch

    default_year_dropdown: ft.Dropdown
    ics_alarm_minutes_dropdown: ft.Dropdown

    # "Application" — prepared, not persisted/bound yet (see PreferencesModel).
    application: PreferencesModel = field(default_factory=PreferencesModel)


def _control_row(
    icon: ft.IconData, label: str, control: ft.Control, *, hint: str | None = None
) -> ft.Control:
    """A real, interactive row — label (+ optional hint line) and a
    control (``ft.Switch``/``ft.Dropdown``) already wired by main_view.py.

    Same bordered-card shell as ``ComingSoonRow`` (Design System/Layout
    System unchanged, per the brief) — only the trailing element differs:
    a real control instead of a static "coming soon" chip.
    """
    label_column: ft.Control
    if hint is None:
        label_column = ft.Text(label, size=theme.FontSize.BODY, color=theme.Colors.TEXT_SECONDARY)
    else:
        label_column = ft.Column(
            controls=[
                ft.Text(label, size=theme.FontSize.BODY, color=theme.Colors.TEXT_SECONDARY),
                ft.Text(hint, size=theme.FontSize.CAPTION, color=theme.Colors.TEXT_MUTED),
            ],
            spacing=theme.Spacing.XXS,
        )
    return theme.card(
        ft.Row(
            controls=[
                ft.Icon(icon, size=theme.IconSize.MD, color=theme.Colors.TEXT_MUTED),
                ft.Container(content=label_column, expand=True),
                control,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=theme.Spacing.SM,
        )
    )


def build_preferences_view(controls: PreferencesViewControls) -> ft.Control:
    """Return the Préférences page, through the Layout System.

    Args:
        controls: pre-built Flet controls (already wired to
            NotificationService/the preferences file by main_view.py) +
            display data — see ``PreferencesViewControls``.
    """
    favorites_hint = STRINGS.favorites_count.format(
        n=controls.favorite_count, s=plural(controls.favorite_count)
    )

    notifications_rows = CardList(
        [
            _control_row(
                ft.Icons.NOTIFICATIONS_OUTLINED,
                STRINGS.prefs_notifications_enabled,
                controls.notifications_enabled_switch,
            ),
            _control_row(
                ft.Icons.STAR_OUTLINE,
                STRINGS.prefs_notifications_favorites_only,
                controls.notifications_favorites_only_switch,
                hint=favorites_hint,
            ),
            _control_row(
                ft.Icons.TIMER_OUTLINED,
                STRINGS.prefs_notifications_lead_time,
                controls.notifications_lead_time_dropdown,
            ),
        ]
    )

    updates_rows = CardList(
        [
            _control_row(
                ft.Icons.SYSTEM_UPDATE_OUTLINED,
                STRINGS.prefs_update_check_enabled,
                controls.update_check_enabled_switch,
            ),
        ]
    )

    calendar_rows = CardList(
        [
            _control_row(
                ft.Icons.CALENDAR_MONTH,
                STRINGS.prefs_default_year,
                controls.default_year_dropdown,
            ),
            _control_row(
                ft.Icons.ALARM,
                STRINGS.prefs_export_reminder,
                controls.ics_alarm_minutes_dropdown,
            ),
        ]
    )

    application_rows = CardList([ComingSoonRow(icon, label) for icon, label, _ in _PREF_ROWS])

    return PageContainer(
        header=PageHeader(STRINGS.prefs_title, icon=ft.Icons.SETTINGS),
        body=[
            Section(
                SectionHeader(
                    STRINGS.prefs_section_notifications, icon=ft.Icons.NOTIFICATIONS_OUTLINED
                ),
                notifications_rows,
            ),
            Section(
                SectionHeader(STRINGS.prefs_section_updates, icon=ft.Icons.SYSTEM_UPDATE_OUTLINED),
                updates_rows,
            ),
            Section(
                SectionHeader(STRINGS.prefs_section_calendar, icon=ft.Icons.CALENDAR_MONTH),
                calendar_rows,
            ),
            Section(
                SectionHeader(STRINGS.prefs_section_application, icon=ft.Icons.TUNE),
                application_rows,
            ),
        ],
    )
