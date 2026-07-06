"""Flet desktop application entry point.

Usage:
    motocal-gui
    python -m motorsport_calendar.gui

Icon customization (Sprint 23 placeholder):
  1. Place your PNG icon at motorsport_calendar/gui/assets/icon.png
  2. Uncomment the assets_dir line below
  3. Set page.window.icon = "icon.png" at the top of build_main_view()
"""

from __future__ import annotations


def main() -> None:
    """Launch the Motorsport Calendar desktop GUI."""
    try:
        import flet as ft
    except ImportError:
        import sys

        sys.exit(
            "Flet is required for the GUI.\n"
            "Install it with:  pip install motorsport-calendar[gui]"
        )

    from motorsport_calendar.gui.main_view import build_main_view

    ft.run(
        main=build_main_view,
        view=ft.AppView.FLET_APP,
        # assets_dir="motorsport_calendar/gui/assets",  # uncomment when icon.png is ready
    )


if __name__ == "__main__":
    main()
