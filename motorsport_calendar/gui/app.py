"""Flet desktop application entry point.

Usage:
    motocal-gui
    python -m motorsport_calendar.gui
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

    ft.run(main=build_main_view, view=ft.AppView.FLET_APP)


if __name__ == "__main__":
    main()
