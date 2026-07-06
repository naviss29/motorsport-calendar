"""Main view — Flet UI for Motorsport Calendar.

Requires flet>=0.80:  pip install motorsport-calendar[gui]
All business logic lives in controller.py — this file contains only presentation.
"""

from __future__ import annotations

from datetime import date

import flet as ft

from motorsport_calendar.gui.controller import generate_calendar, list_championships
from motorsport_calendar.gui.models import GenerateState


async def build_main_view(page: ft.Page) -> None:
    """Build and attach the main view to the Flet page."""
    page.title = "Motorsport Calendar"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    # --- State ---
    state = GenerateState(year=date.today().year)

    # --- Year selector ---
    current_year = date.today().year
    year_options = [
        ft.dropdown.Option(str(y))
        for y in range(current_year - 5, current_year + 6)
    ]

    def on_year_change(e: ft.ControlEvent) -> None:
        state.year = int(e.control.value)

    year_dropdown = ft.Dropdown(
        label="Saison",
        value=str(current_year),
        options=year_options,
        width=180,
        on_change=on_year_change,
    )

    # --- Championship checkboxes ---
    championships = list_championships()
    checkboxes: dict[str, ft.Checkbox] = {}

    def _make_on_change(cid: str) -> ft.ControlEvent:
        def handler(e: ft.ControlEvent) -> None:
            if e.control.value and cid not in state.selected_championships:
                state.selected_championships.append(cid)
            elif not e.control.value and cid in state.selected_championships:
                state.selected_championships.remove(cid)
            _refresh_button()

        return handler

    for cid in championships:
        checkboxes[cid] = ft.Checkbox(
            label=cid,
            value=False,
            on_change=_make_on_change(cid),
        )

    # --- Output path ---
    output_field = ft.TextField(
        label="Fichier de sortie (.ics)",
        hint_text="Cliquer sur l'icône pour choisir…",
        read_only=True,
        expand=True,
        dense=True,
    )

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    async def on_browse_click(e: ft.ControlEvent) -> None:
        result = await file_picker.save_file(
            dialog_title="Enregistrer le calendrier ICS",
            file_name="calendrier.ics",
            allowed_extensions=["ics"],
        )
        if result:
            path = result if result.endswith(".ics") else f"{result}.ics"
            state.output_path = path
            output_field.value = path
            _refresh_button()
            page.update()

    browse_btn = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        tooltip="Choisir le fichier de sortie",
        on_click=on_browse_click,
    )

    # --- Status area ---
    status_text = ft.Text(
        value="",
        size=13,
        color=ft.Colors.WHITE70,
        selectable=True,
    )
    progress_ring = ft.ProgressRing(width=22, height=22, visible=False)

    # --- Generate button ---
    generate_btn = ft.Button(
        text="Générer",
        icon=ft.Icons.CALENDAR_MONTH,
        disabled=True,
        on_click=None,  # assigned below
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
        ),
    )

    def _refresh_button() -> None:
        generate_btn.disabled = not state.is_ready()
        page.update()

    async def on_generate_click(e: ft.ControlEvent) -> None:
        if not state.is_ready():
            return

        state.is_generating = True
        generate_btn.disabled = True
        progress_ring.visible = True
        status_text.value = "Génération en cours…"
        status_text.color = ft.Colors.WHITE70
        page.update()

        try:
            results = await generate_calendar(
                year=state.year,
                championship_ids=list(state.selected_championships),
                output_path=state.output_path,
                refresh=False,
            )

            lines: list[str] = []
            total_events = 0
            for cid, val in results.items():
                if isinstance(val, int):
                    lines.append(
                        f"✓ {cid} : {val} événement{'s' if val != 1 else ''}"
                    )
                    total_events += val
                else:
                    lines.append(f"✗ {cid} : {val}")

            success = any(isinstance(v, int) for v in results.values())
            if success:
                status_text.value = (
                    f"✓ Export terminé — {total_events} "
                    f"événement{'s' if total_events != 1 else ''}\n"
                    + "\n".join(lines)
                )
                status_text.color = ft.Colors.GREEN_400
            else:
                status_text.value = "✗ Aucun événement exporté\n" + "\n".join(lines)
                status_text.color = ft.Colors.RED_400

        except Exception as exc:  # noqa: BLE001
            status_text.value = f"✗ Erreur inattendue : {exc}"
            status_text.color = ft.Colors.RED_400
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
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SPORTS_MOTORSPORTS, size=28, color=ft.Colors.RED_400),
                        ft.Text(
                            "Motorsport Calendar",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Génération de calendriers ICS",
                    size=13,
                    color=ft.Colors.WHITE54,
                ),
                ft.Divider(height=20),

                # Year
                ft.Text("Saison", size=14, weight=ft.FontWeight.W_500),
                year_dropdown,
                ft.Divider(height=12),

                # Championships
                ft.Text("Championnats", size=14, weight=ft.FontWeight.W_500),
                ft.Column(
                    controls=[checkboxes[cid] for cid in championships],
                    spacing=2,
                ),
                ft.Divider(height=12),

                # Output file
                ft.Text("Fichier de sortie", size=14, weight=ft.FontWeight.W_500),
                ft.Row([output_field, browse_btn], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=20),

                # Action row
                ft.Row(
                    [generate_btn, progress_ring],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                ),
                ft.Divider(height=10),

                # Status
                status_text,
            ],
            spacing=8,
            width=480,
        )
    )
