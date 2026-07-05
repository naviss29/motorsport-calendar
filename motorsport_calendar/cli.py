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


@app.command("generate-f1")
def generate_f1(
    year: Annotated[int, typer.Argument(help="Formula 1 season year (e.g. 2024)")],
    output: Annotated[Path, typer.Argument(help="Destination .ics file")],
    refresh: Annotated[
        bool,
        typer.Option("--refresh", help="Ignorer le cache et re-télécharger les données."),
    ] = False,
) -> None:
    """Fetch the Formula 1 calendar via OpenF1 and export it as an ICS file."""
    import asyncio

    import httpx

    from motorsport_calendar.exporters.ics import IcsExporter
    from motorsport_calendar.providers.formula1.provider import Formula1Provider
    from motorsport_calendar.providers.formula1.sources.openf1 import OpenF1Source

    async def _fetch() -> list:
        source = OpenF1Source(refresh=refresh)
        provider = Formula1Provider(source)
        return await provider.fetch_events("formula1", year)

    cache_note = " [yellow](--refresh : cache ignoré)[/]" if refresh else ""
    console.print(f"Fetching F1 [bold cyan]{year}[/] calendar from OpenF1…{cache_note}")

    try:
        events = asyncio.run(_fetch())
    except httpx.HTTPStatusError as exc:
        err_console.print(
            f"OpenF1 API error {exc.response.status_code}: {exc.request.url}"
        )
        raise typer.Exit(code=1)
    except httpx.TimeoutException:
        err_console.print("OpenF1 API timeout (10 s). Try again later.")
        raise typer.Exit(code=1)

    IcsExporter().export(events, output)

    count = len(events)
    sessions_count = sum(len(e.sessions) for e in events)
    console.print(
        f"[green]✓[/] {count} event{'s' if count != 1 else ''}, "
        f"{sessions_count} session{'s' if sessions_count != 1 else ''} → [bold]{output}[/]"
    )


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
