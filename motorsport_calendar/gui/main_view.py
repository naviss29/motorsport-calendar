"""Main view — Flet UI for Motorsport Calendar.

Requires flet>=0.80:  pip install motorsport-calendar[gui]

Design rules:
- All user-visible text comes from strings.py (STRINGS singleton).
- Championship labels come from display_names.py (get_display_name).
- User preferences (selected championships, last output dir) are persisted via preferences.py.
- All business logic stays in controller.py — this file contains only presentation.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

import flet as ft

from motorsport_calendar.gui.controller import generate_calendar, list_championships
from motorsport_calendar.gui.display_names import DEFAULT_SELECTED, get_display_name
from motorsport_calendar.gui.models import GenerateState
from motorsport_calendar.gui.preferences import load_preferences, save_preferences
from motorsport_calendar.gui.strings import STRINGS, plural


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
    """Build and attach the main view to the Flet page."""
    page.title = STRINGS.app_title
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO
    page.window.min_width = 520
    page.window.min_height = 580
    page.window.width = 560
    page.window.height = 700

    # --- Preferences ---
    prefs = load_preferences()

    def _save_prefs() -> None:
        save_preferences({
            "selected_championships": list(state.selected_championships),
            "last_output_dir": prefs.get("last_output_dir", ""),
        })

    # --- State ---
    state = GenerateState(
        year=date.today().year,
        selected_championships=list(
            prefs.get("selected_championships", DEFAULT_SELECTED)
        ),
    )

    # --- Year selector ---
    current_year = date.today().year
    year_options = [
        ft.dropdown.Option(str(y))
        for y in range(current_year - 5, current_year + 6)
    ]

    def on_year_change(e: ft.ControlEvent) -> None:
        state.year = int(e.control.value)
        _refresh_button()

    year_dropdown = ft.Dropdown(
        label=STRINGS.season_label,
        value=str(current_year),
        options=year_options,
        width=180,
        on_select=on_year_change,
    )

    # --- Championship checkboxes ---
    championships = list_championships()
    checkboxes: dict[str, ft.Checkbox] = {}

    def _make_on_change(cid: str):
        def handler(e: ft.ControlEvent) -> None:
            if e.control.value and cid not in state.selected_championships:
                state.selected_championships.append(cid)
            elif not e.control.value and cid in state.selected_championships:
                state.selected_championships.remove(cid)
            _save_prefs()
            _refresh_button()

        return handler

    for cid in championships:
        checkboxes[cid] = ft.Checkbox(
            label=get_display_name(cid),
            value=cid in state.selected_championships,
            on_change=_make_on_change(cid),
        )

    # --- Output path ---
    output_field = ft.TextField(
        label=STRINGS.output_label,
        hint_text=STRINGS.output_hint,
        read_only=True,
        expand=True,
        dense=True,
    )

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

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
            _refresh_button()
            page.update()

    browse_btn = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        tooltip=STRINGS.browse_tooltip,
        on_click=on_browse_click,
    )

    # --- Progress ring ---
    progress_ring = ft.ProgressRing(width=22, height=22, visible=False)

    # --- Generate button ---
    generate_btn = ft.Button(
        content=STRINGS.generate_btn,
        icon=ft.Icons.CALENDAR_MONTH,
        disabled=True,
        on_click=None,  # assigned below
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
        ),
    )

    # --- Error text (shown only on failure) ---
    error_text = ft.Text(value="", size=13, color=ft.Colors.RED_400, selectable=True)

    def _refresh_button() -> None:
        generate_btn.disabled = not state.is_ready()
        page.update()

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
                        ft.Text(
                            STRINGS.success_saved_at,
                            size=12,
                            color=ft.Colors.WHITE70,
                        ),
                        ft.Text(
                            output_path,
                            size=11,
                            selectable=True,
                            color=ft.Colors.WHITE54,
                        ),
                        ft.Divider(height=8),
                        ft.Text(
                            "\n".join(details),
                            size=12,
                            color=ft.Colors.WHITE70,
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
                ft.Button(
                    content=STRINGS.close_btn,
                    on_click=on_close,
                ),
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
                    details.append(
                        STRINGS.summary_error.format(name=name, err=val)
                    )

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

    # --- Layout ---
    page.add(
        ft.Column(
            controls=[
                # Header
                # Icon placeholder — replace ft.Icon with ft.Image when the app logo is ready:
                #   ft.Image(src="icon.png", width=32, height=32)
                # Place the PNG in motorsport_calendar/gui/assets/ and pass
                #   assets_dir="motorsport_calendar/gui/assets" to ft.run() in app.py
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=30, color=ft.Colors.RED_400),
                        ft.Column(
                            [
                                ft.Text(
                                    STRINGS.app_title,
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    STRINGS.app_subtitle,
                                    size=12,
                                    color=ft.Colors.WHITE54,
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=20),

                # Season
                ft.Text(STRINGS.season_label, size=14, weight=ft.FontWeight.W_500),
                year_dropdown,
                ft.Divider(height=12),

                # Championships
                ft.Text(STRINGS.championships_label, size=14, weight=ft.FontWeight.W_500),
                ft.Column(
                    controls=[checkboxes[cid] for cid in championships],
                    spacing=2,
                ),
                ft.Divider(height=12),

                # Output file
                ft.Text(STRINGS.output_label, size=14, weight=ft.FontWeight.W_500),
                ft.Row(
                    [output_field, browse_btn],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=20),

                # Action row
                ft.Row(
                    [generate_btn, progress_ring],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                ),
                ft.Divider(height=8),

                # Error / status text
                error_text,
            ],
            spacing=8,
            width=480,
        )
    )
