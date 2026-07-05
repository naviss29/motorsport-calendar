"""CLI entry point — no business logic, only presentation and delegation."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="motocal",
    help="[bold green]motorsport-calendar[/] — Generate motorsport calendars in ICS format.",
    add_completion=True,
    rich_markup_mode="rich",
)
console = Console()
err_console = Console(stderr=True, style="red")


def _version_callback(value: bool) -> None:
    if value:
        from motorsport_calendar import __version__

        console.print(f"motocal [bold green]v{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
) -> None:
    """motorsport-calendar — Generate motorsport race calendars in ICS format."""


@app.command()
def version() -> None:
    """Show the current version."""
    from motorsport_calendar import __version__

    console.print(f"motocal [bold green]v{__version__}[/]")


@app.command()
def providers() -> None:
    """List all registered data providers."""
    table = Table(title="Registered Providers", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Championships", style="white")

    # Populated once providers are implemented
    console.print(table)
    console.print("[yellow]No providers registered yet.[/]")


@app.command()
def export(
    provider: Annotated[str, typer.Option("--provider", "-p", help="Data provider name")],
    championship: Annotated[str, typer.Option("--championship", "-c", help="Championship ID")],
    year: Annotated[int, typer.Option("--year", "-y", help="Season year")],
    exporter: Annotated[
        str, typer.Option("--exporter", "-e", help="Output format (default: ics)")
    ] = "ics",
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output file path", writable=True),
    ] = Path("calendar.ics"),
) -> None:
    """Export a motorsport championship calendar to a file."""
    console.print(
        f"[bold]Exporting[/] [cyan]{championship}[/] [bold]{year}[/]"
        f" via [green]{provider}[/] → [yellow]{output}[/]"
    )
    err_console.print("No providers are registered yet.")
    raise typer.Exit(code=1)
