"""Main view — Flet UI for Motorsport Calendar.

Requires flet>=0.80:  pip install motorsport-calendar[gui]

Design rules:
- All user-visible text comes from strings.py (STRINGS singleton).
- Championship labels come from display_names.py (get_display_name).
- Championship groups come from categories.py (get_groups_for).
- User preferences (selected championships, last output dir) are persisted via preferences.py.
- All business logic stays in controller.py — this file contains only presentation.
- Views are built once at startup and swapped via NavigationRail without rebuilding.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

import flet as ft

from motorsport_calendar.gui.categories import get_groups_for
from motorsport_calendar.gui.controller import generate_calendar, list_championships
from motorsport_calendar.gui.display_names import DEFAULT_SELECTED, get_display_name
from motorsport_calendar.gui.models import GenerateState
from motorsport_calendar.gui.preferences import load_preferences, save_preferences
from motorsport_calendar.gui.strings import STRINGS, plural

# Public GitHub URL for the About screen
_GITHUB_URL = "https://github.com/naviss29/motorsport-calendar"


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
    page.padding = 0
    page.window.min_width = 560
    page.window.min_height = 580
    page.window.width = 700
    page.window.height = 720

    # --- Services ---
    file_picker = ft.FilePicker()
    url_launcher = ft.UrlLauncher()
    page.services.extend([file_picker, url_launcher])

    # --- Preferences + State ---
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
    # SHARED CONTROLS (used across multiple views)
    # =========================================================================

    # --- Year selector (calendar view) ---
    current_year = date.today().year
    year_options = [
        ft.dropdown.Option(str(y))
        for y in range(current_year - 5, current_year + 6)
    ]

    def on_year_change(e: ft.ControlEvent) -> None:
        state.year = int(e.control.value)
        _refresh_generate_btn()

    year_dropdown = ft.Dropdown(
        label=STRINGS.season_label,
        value=str(current_year),
        options=year_options,
        width=180,
        on_select=on_year_change,
    )

    # --- Championship checkboxes (calendar view) ---
    championships = list_championships()
    checkboxes: dict[str, ft.Checkbox] = {}

    def _make_on_change(cid: str):
        def handler(e: ft.ControlEvent) -> None:
            if e.control.value and cid not in state.selected_championships:
                state.selected_championships.append(cid)
            elif not e.control.value and cid in state.selected_championships:
                state.selected_championships.remove(cid)
            _save_prefs()
            _refresh_generate_btn()
        return handler

    for cid in championships:
        checkboxes[cid] = ft.Checkbox(
            label=get_display_name(cid),
            value=cid in state.selected_championships,
            on_change=_make_on_change(cid),
        )

    # --- Output path (calendar view) ---
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
            _refresh_generate_btn()
            page.update()

    browse_btn = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        tooltip=STRINGS.browse_tooltip,
        on_click=on_browse_click,
    )

    # --- Generate button & progress (calendar view) ---
    progress_ring = ft.ProgressRing(width=22, height=22, visible=False)
    error_text = ft.Text(value="", size=13, color=ft.Colors.RED_400, selectable=True)

    generate_btn = ft.Button(
        content=STRINGS.generate_btn,
        icon=ft.Icons.CALENDAR_MONTH,
        disabled=True,
        on_click=None,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
        ),
    )

    def _refresh_generate_btn() -> None:
        generate_btn.disabled = not state.is_ready()
        page.update()

    # --- Success dialog (calendar view) ---
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
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREEN_400,
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"{total_events} événement{ev_s}  ·  "
                            f"{total_sessions} session{sess_s}",
                            size=15,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Divider(height=8),
                        ft.Text(STRINGS.success_saved_at, size=12, color=ft.Colors.WHITE70),
                        ft.Text(output_path, size=11, selectable=True, color=ft.Colors.WHITE54),
                        ft.Divider(height=8),
                        ft.Text("\n".join(details), size=12, color=ft.Colors.WHITE70),
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
        error_text.color = ft.Colors.WHITE70
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
                error_text.color = ft.Colors.RED_400

        except Exception as exc:  # noqa: BLE001
            error_text.value = STRINGS.error_unexpected.format(msg=exc)
            error_text.color = ft.Colors.RED_400
        finally:
            state.is_generating = False
            generate_btn.disabled = not state.is_ready()
            progress_ring.visible = False
            page.update()

    generate_btn.on_click = on_generate_click

    # =========================================================================
    # VIEW BUILDERS
    # =========================================================================

    def _build_home_view(on_cta_click) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        [ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=56, color=ft.Colors.RED_400)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        STRINGS.home_title,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        STRINGS.app_subtitle,
                        size=14,
                        color=ft.Colors.WHITE54,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=16),
                    ft.Container(
                        content=ft.Text(
                            STRINGS.home_body,
                            size=14,
                            color=ft.Colors.WHITE70,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        width=480,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(height=24),
                    ft.Row(
                        [
                            ft.Button(
                                content=STRINGS.home_cta,
                                icon=ft.Icons.CALENDAR_MONTH,
                                on_click=on_cta_click,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_700,
                                    color=ft.Colors.WHITE,
                                ),
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            expand=True,
            padding=ft.Padding.all(32),
            alignment=ft.Alignment.TOP_CENTER,
        )

    def _build_championship_groups() -> list[ft.Control]:
        """Return grouped checkbox rows with visual section headers."""
        groups = get_groups_for(championships)
        controls: list[ft.Control] = []
        for i, (group, ids) in enumerate(groups):
            if i > 0:
                controls.append(ft.Divider(height=8))
            controls.append(
                ft.Text(
                    f"{group.emoji}  {group.label}",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE60,
                )
            )
            for cid in ids:
                controls.append(checkboxes[cid])
        return controls

    def _build_calendar_view() -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=24, color=ft.Colors.RED_400),
                            ft.Text(
                                STRINGS.app_title,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=16),

                    # Saison
                    ft.Text(STRINGS.season_label, size=13, weight=ft.FontWeight.W_500),
                    year_dropdown,
                    ft.Divider(height=10),

                    # Championnats (groupés)
                    ft.Text(STRINGS.championships_label, size=13, weight=ft.FontWeight.W_500),
                    ft.Column(
                        controls=_build_championship_groups(),
                        spacing=2,
                    ),
                    ft.Divider(height=10),

                    # Fichier de sortie
                    ft.Text(STRINGS.output_label, size=13, weight=ft.FontWeight.W_500),
                    ft.Row(
                        [output_field, browse_btn],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=16),

                    # Action
                    ft.Row(
                        [generate_btn, progress_ring],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=14,
                    ),
                    ft.Divider(height=6),
                    error_text,
                ],
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=ft.Padding.symmetric(vertical=24, horizontal=28),
        )

    def _build_about_view() -> ft.Control:
        async def on_github_click(e: ft.ControlEvent) -> None:
            try:
                await url_launcher.launch_url(_GITHUB_URL)
            except Exception:  # noqa: BLE001
                # Fallback for environments where UrlLauncher may not work
                if sys.platform == "win32":
                    subprocess.Popen(["start", "", _GITHUB_URL], shell=True)  # noqa: S603,S607

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

    # =========================================================================
    # NAVIGATION SHELL
    # =========================================================================

    views: list[ft.Control] = []  # populated after builds below

    def on_nav_change(e: ft.ControlEvent) -> None:
        idx = int(e.control.selected_index)
        content_area.content = views[idx]
        page.update()

    nav_rail = ft.NavigationRail(
        selected_index=1,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=72,
        extended=page.width > 900 if page.width else False,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label=STRINGS.nav_home,
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label=STRINGS.nav_calendar,
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

    # Build views after nav_rail exists (on_cta_click needs nav_rail)
    def on_home_cta_click(e: ft.ControlEvent) -> None:
        nav_rail.selected_index = 1
        content_area.content = views[1]
        page.update()

    home_view = _build_home_view(on_home_cta_click)
    calendar_view = _build_calendar_view()
    about_view = _build_about_view()

    views.extend([home_view, calendar_view, about_view])

    content_area = ft.Container(
        content=views[1],  # start on Calendar
        expand=True,
    )

    page.add(
        ft.Row(
            controls=[
                nav_rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
    )
