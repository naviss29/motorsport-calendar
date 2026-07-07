"""Main view — Flet navigation shell for Motorsport Calendar.

Requires flet>=0.80:  pip install motorsport-calendar[gui]

Responsibilities:
- Page setup, services, window sizing
- NavigationRail (5 destinations)
- Shared state + handlers for the calendar wizard (Mon calendrier)
- Delegates layout to motorsport_calendar.gui.views.*
- Delegates visual tokens (colors, spacing, radii) to motorsport_calendar.gui.theme

Design rules:
- All user-visible text comes from strings.py (STRINGS singleton).
- All colors/spacing/radii come from theme.py — nothing hardcoded here.
- Championship labels come from display_names.py (get_display_name).
- Championship groups come from categories.py (get_groups_for).
- Preferences file I/O uses preferences.py.
- Each view is an independent ft.Control; swapped on nav change without rebuilding.
- The calendar wizard is one exception: its container's `.content` is
  rebuilt on every step change (see `_refresh_calendar_view`), since each
  step renders different controls.
- Ce week-end is the other exception (Sprint 29): it starts in the loading
  state and its container's `.content` is replaced once when the background
  fetch (`_load_weekend`) resolves — never re-fetched on every tab visit.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from datetime import date
from pathlib import Path

import flet as ft

from motorsport_calendar.gui import theme
from motorsport_calendar.gui.categories import get_groups_for
from motorsport_calendar.gui.controller import (
    generate_calendar,
    get_upcoming_weekend,
    list_championships,
)
from motorsport_calendar.gui.display_names import DEFAULT_SELECTED, get_display_name
from motorsport_calendar.gui.models import GenerateState, PreferencesModel
from motorsport_calendar.gui.preferences import load_preferences, save_preferences
from motorsport_calendar.gui.strings import STRINGS, plural
from motorsport_calendar.gui.views.about import build_about_view
from motorsport_calendar.gui.views.calendar import CalendarViewControls, build_calendar_view
from motorsport_calendar.gui.views.favorites import build_favorites_view
from motorsport_calendar.gui.views.preferences import build_preferences_view
from motorsport_calendar.gui.views.weekend import build_weekend_view


def _open_folder(path: str) -> None:
    """Open the folder containing *path* in the system file manager."""
    folder = str(Path(path).parent)
    try:
        if sys.platform == "win32":
            subprocess.Popen(["explorer", folder])  # noqa: S603,S607
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])  # noqa: S603,S607
        else:
            subprocess.Popen(["xdg-open", folder])  # noqa: S603,S607
    except OSError:
        pass


async def build_main_view(page: ft.Page) -> None:  # noqa: C901
    """Build and attach the navigation shell + all views to the Flet page."""
    page.title = STRINGS.app_title
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = theme.Colors.BACKGROUND
    page.padding = 0
    page.window.min_width = 560
    page.window.min_height = 580
    page.window.width = 700
    page.window.height = 720

    # =========================================================================
    # SERVICES
    # =========================================================================

    file_picker = ft.FilePicker()
    url_launcher = ft.UrlLauncher()
    page.services.extend([file_picker, url_launcher])

    # =========================================================================
    # PREFERENCES + STATE (calendar wizard only)
    # =========================================================================

    prefs = load_preferences()

    def _save_prefs() -> None:
        save_preferences({
            "selected_championships": list(state.selected_championships),
            "last_output_dir": prefs.get("last_output_dir", ""),
        })

    state = GenerateState(
        year=date.today().year,
        selected_championships=list(
            prefs.get("selected_championships", DEFAULT_SELECTED)
        ),
    )

    # =========================================================================
    # CALENDAR WIZARD CONTROLS (state + handlers stay here; layout in views/)
    # =========================================================================

    calendar_container = ft.Container(expand=True)

    # --- Year selector (step 1) ---
    current_year = date.today().year

    def on_year_change(e: ft.ControlEvent) -> None:
        state.year = int(e.control.value)
        _refresh_calendar_view()

    year_dropdown = ft.Dropdown(
        label=STRINGS.season_label,
        value=str(current_year),
        options=[
            ft.dropdown.Option(str(y))
            for y in range(current_year - 5, current_year + 6)
        ],
        width=220,
        on_select=on_year_change,
    )

    # --- Championship checkboxes, grouped (step 2) ---
    championships = list_championships()
    checkboxes: dict[str, ft.Checkbox] = {}

    def _make_on_change(cid: str):
        def handler(e: ft.ControlEvent) -> None:
            if e.control.value and cid not in state.selected_championships:
                state.selected_championships.append(cid)
            elif not e.control.value and cid in state.selected_championships:
                state.selected_championships.remove(cid)
            _save_prefs()
            _refresh_calendar_view()
        return handler

    for cid in championships:
        checkboxes[cid] = ft.Checkbox(
            label=get_display_name(cid),
            value=cid in state.selected_championships,
            on_change=_make_on_change(cid),
        )

    def _build_championship_groups() -> list[ft.Control]:
        groups = get_groups_for(championships)
        controls: list[ft.Control] = []
        for i, (group, ids) in enumerate(groups):
            if i > 0:
                controls.append(ft.Divider(height=theme.Spacing.XS))
            controls.append(
                ft.Text(
                    f"{group.emoji}  {group.label}",
                    size=theme.FontSize.SMALL,
                    weight=ft.FontWeight.W_600,
                    color=theme.Colors.TEXT_MUTED,
                )
            )
            for cid in ids:
                controls.append(checkboxes[cid])
        return controls

    # --- Output path (step 3) ---
    output_field = ft.TextField(
        label=STRINGS.output_label,
        hint_text=STRINGS.output_hint,
        read_only=True,
        expand=True,
        dense=True,
    )

    async def on_browse_click(e: ft.ControlEvent) -> None:
        last_dir = prefs.get("last_output_dir") or None
        result = await file_picker.save_file(
            dialog_title=STRINGS.save_dialog_title,
            file_name=f"motorsport-calendar-{state.year}.ics",
            initial_directory=last_dir,
            allowed_extensions=["ics"],
        )
        if result:
            path = result if result.endswith(".ics") else f"{result}.ics"
            state.output_path = path
            output_field.value = path
            prefs["last_output_dir"] = str(Path(path).parent)
            _save_prefs()
            _refresh_calendar_view()

    browse_btn = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        tooltip=STRINGS.browse_tooltip,
        on_click=on_browse_click,
    )

    # --- Generate button & progress (step 4) ---
    progress_ring = ft.ProgressRing(width=22, height=22, visible=False)
    error_text = ft.Text(
        value="", size=theme.FontSize.BODY, color=theme.Colors.ERROR, selectable=True
    )

    generate_btn = ft.Button(
        content=STRINGS.generate_btn,
        icon=ft.Icons.CALENDAR_MONTH,
        disabled=True,
        on_click=None,
        style=theme.button_style("cta"),
    )

    def _refresh_generate_btn() -> None:
        generate_btn.disabled = not state.is_ready()

    # --- Wizard navigation (back / next / step click) ---

    def _recap_row(label: str, value: str, step: int) -> ft.Control:
        def _edit(e: ft.ControlEvent) -> None:
            on_step_click(step)

        return theme.card(
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                label,
                                size=theme.FontSize.CAPTION,
                                color=theme.Colors.TEXT_MUTED,
                            ),
                            ft.Text(
                                value, size=theme.FontSize.BODY, weight=ft.FontWeight.W_500
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.TextButton(content=STRINGS.wizard_edit_btn, on_click=_edit),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def _build_recap_controls() -> list[ft.Control]:
        names = [get_display_name(cid) for cid in state.selected_championships]
        champ_value = ", ".join(names) if names else STRINGS.wizard_recap_none
        return [
            _recap_row(STRINGS.wizard_recap_season, str(state.year), 0),
            _recap_row(STRINGS.wizard_recap_championships, champ_value, 1),
            _recap_row(
                STRINGS.wizard_recap_destination,
                state.output_path or STRINGS.wizard_recap_none,
                2,
            ),
        ]

    def _current_calendar_controls() -> CalendarViewControls:
        return CalendarViewControls(
            year_dropdown=year_dropdown,
            output_field=output_field,
            browse_btn=browse_btn,
            generate_btn=generate_btn,
            progress_ring=progress_ring,
            error_text=error_text,
            back_btn=back_btn,
            next_btn=next_btn,
            championship_groups=_build_championship_groups(),
            recap_controls=_build_recap_controls(),
            current_step=state.current_step,
            on_step_click=on_step_click,
        )

    def _refresh_calendar_view() -> None:
        _refresh_generate_btn()
        next_btn.disabled = not state.can_advance()
        calendar_container.content = build_calendar_view(_current_calendar_controls())
        page.update()

    def on_wizard_next(e: ft.ControlEvent) -> None:
        if state.can_advance():
            state.current_step += 1
            _refresh_calendar_view()

    def on_wizard_back(e: ft.ControlEvent) -> None:
        if state.can_go_back():
            state.current_step -= 1
            _refresh_calendar_view()

    def on_step_click(step: int) -> None:
        if step <= state.current_step:
            state.current_step = step
            _refresh_calendar_view()

    back_btn = ft.Button(
        content=STRINGS.wizard_back_btn,
        icon=ft.Icons.ARROW_BACK,
        on_click=on_wizard_back,
        style=theme.button_style("ghost"),
    )
    next_btn = ft.Button(
        content=STRINGS.wizard_next_btn,
        icon=ft.Icons.ARROW_FORWARD,
        on_click=on_wizard_next,
        style=theme.button_style("primary"),
    )

    # --- Success dialog ---
    def _show_success_dialog(
        total_events: int,
        total_sessions: int,
        output_path: str,
        details: list[str],
    ) -> None:
        ev_s = plural(total_events)
        sess_s = plural(total_sessions)

        def on_open_folder(e: ft.ControlEvent) -> None:
            _open_folder(output_path)

        def on_close(e: ft.ControlEvent) -> None:
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text(
                f"✅  {STRINGS.success_title}",
                size=theme.FontSize.HEADLINE,
                weight=ft.FontWeight.BOLD,
                color=theme.Colors.SUCCESS,
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"{total_events} événement{ev_s}  ·  "
                            f"{total_sessions} session{sess_s}",
                            size=theme.FontSize.SUBTITLE,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Divider(height=theme.Spacing.XS),
                        ft.Text(
                            STRINGS.success_saved_at,
                            size=theme.FontSize.SMALL,
                            color=theme.Colors.TEXT_SECONDARY,
                        ),
                        ft.Text(
                            output_path,
                            size=theme.FontSize.CAPTION,
                            selectable=True,
                            color=theme.Colors.TEXT_MUTED,
                        ),
                        ft.Divider(height=theme.Spacing.XS),
                        ft.Text(
                            "\n".join(details),
                            size=theme.FontSize.SMALL,
                            color=theme.Colors.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=4,
                ),
                width=400,
            ),
            actions=[
                ft.Button(
                    content=STRINGS.open_folder_btn,
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=on_open_folder,
                ),
                ft.Button(content=STRINGS.close_btn, on_click=on_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    # --- Generate handler ---
    async def on_generate_click(e: ft.ControlEvent) -> None:
        if not state.is_ready():
            return

        state.is_generating = True
        generate_btn.disabled = True
        progress_ring.visible = True
        error_text.value = STRINGS.generating_status
        error_text.color = theme.Colors.TEXT_SECONDARY
        page.update()

        try:
            results = await generate_calendar(
                year=state.year,
                championship_ids=list(state.selected_championships),
                output_path=state.output_path,
                refresh=False,
            )

            total_events = 0
            total_sessions = 0
            details: list[str] = []
            has_success = False

            for cid, val in results.items():
                name = get_display_name(cid)
                if isinstance(val, tuple):
                    n_ev, n_sess = val
                    total_events += n_ev
                    total_sessions += n_sess
                    details.append(
                        STRINGS.summary_ok.format(name=name, n=n_ev, s=plural(n_ev))
                    )
                    has_success = True
                else:
                    details.append(STRINGS.summary_error.format(name=name, err=val))

            error_text.value = ""
            page.update()

            if has_success:
                _show_success_dialog(total_events, total_sessions, state.output_path, details)
            else:
                error_text.value = STRINGS.error_no_events + "\n" + "\n".join(details)
                error_text.color = theme.Colors.ERROR

        except Exception as exc:  # noqa: BLE001
            error_text.value = STRINGS.error_unexpected.format(msg=exc)
            error_text.color = theme.Colors.ERROR
        finally:
            state.is_generating = False
            generate_btn.disabled = not state.is_ready()
            progress_ring.visible = False
            page.update()

    generate_btn.on_click = on_generate_click

    # =========================================================================
    # BUILD ALL VIEWS
    # =========================================================================

    prefs_model = PreferencesModel()

    _refresh_generate_btn()
    next_btn.disabled = not state.can_advance()
    calendar_container.content = build_calendar_view(_current_calendar_controls())

    weekend_container = ft.Container(content=build_weekend_view(None), expand=True)

    async def _load_weekend() -> None:
        """Fetch once per app launch — never on every tab visit.

        The existing HttpCache TTL (see controller.get_upcoming_weekend)
        already prevents redundant network calls; this background task
        just means the fetch starts immediately at launch instead of
        waiting for the user to click the Ce week-end tab.
        """
        try:
            result = await get_upcoming_weekend()
        except Exception:  # never crash the app on this background fetch
            return
        weekend_container.content = build_weekend_view(result)
        page.update()

    # Keep a reference on `page` for the app's lifetime — an unreferenced
    # asyncio.Task can be garbage-collected mid-flight.
    page.weekend_load_task = asyncio.create_task(_load_weekend())

    all_views: list[ft.Control] = [
        weekend_container,
        calendar_container,
        build_favorites_view(),
        build_preferences_view(prefs_model),
        build_about_view(url_launcher),
    ]

    # =========================================================================
    # NAVIGATION SHELL
    # =========================================================================

    def on_nav_change(e: ft.ControlEvent) -> None:
        content_area.content = all_views[int(e.control.selected_index)]
        page.update()

    nav_rail = ft.NavigationRail(
        selected_index=1,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=72,
        extended=False,
        bgcolor=theme.Colors.SURFACE,
        indicator_color=theme.Colors.PRIMARY,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.SPORTS_MOTORSPORTS_OUTLINED,
                selected_icon=ft.Icons.SPORTS_MOTORSPORTS,
                label=STRINGS.nav_weekend,
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label=STRINGS.nav_my_calendar,
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.STAR_OUTLINE,
                selected_icon=ft.Icons.STAR,
                label=STRINGS.nav_favorites,
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label=STRINGS.nav_preferences,
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INFO_OUTLINED,
                selected_icon=ft.Icons.INFO,
                label=STRINGS.nav_about,
            ),
        ],
        on_change=on_nav_change,
    )

    def on_page_resize(e) -> None:
        extended = page.width > 900
        if nav_rail.extended != extended:
            nav_rail.extended = extended
            page.update()

    page.on_resize = on_page_resize

    content_area = ft.Container(
        content=all_views[1],  # start on Mon calendrier
        expand=True,
    )

    page.add(
        ft.Row(
            controls=[
                nav_rail,
                ft.VerticalDivider(width=1, color=theme.Colors.BORDER),
                content_area,
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
    )
