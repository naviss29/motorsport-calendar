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
    from motorsport_calendar.core.registry import registry

    registry.discover()
    all_ids = registry.list_all()

    table = Table(title="Registered Providers", show_header=True, header_style="bold cyan")
    table.add_column("Championship ID", style="green")

    if not all_ids:
        console.print(table)
        console.print("[yellow]No providers registered.[/]")
        return

    for cid in all_ids:
        table.add_row(cid)
    console.print(table)


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

    from motorsport_calendar.cache import HttpCache
    from motorsport_calendar.config import ConfigService
    from motorsport_calendar.core.registry import registry
    from motorsport_calendar.exporters.ics import IcsExporter

    config = ConfigService()

    cache: HttpCache | None = None
    if config.cache.enabled:
        cache = HttpCache(
            cache_dir=config.cache.resolved_path,
            ttl=config.cache.ttl_seconds,
        )

    # Découverte et sélection du provider via le registre — la CLI ne connaît pas les providers
    registry.discover()

    try:
        make_provider = registry.get("formula1")
    except KeyError as exc:
        err_console.print(str(exc))
        raise typer.Exit(code=1)

    provider_cfg = config.providers.get("formula1")
    if provider_cfg is None:
        from motorsport_calendar.config.models import ProviderConfig
        provider_cfg = ProviderConfig(source="openf1")

    try:
        provider = make_provider(provider_cfg, cache, refresh)
    except ValueError as exc:
        err_console.print(str(exc))
        raise typer.Exit(code=1)

    async def _fetch() -> list:
        return await provider.fetch_events("formula1", year)

    source_label = provider_cfg.source or "openf1"
    cache_note = " [yellow](--refresh)[/]" if refresh else ""
    console.print(
        f"Fetching F1 [bold cyan]{year}[/] calendar "
        f"via [green]{source_label}[/]…{cache_note}"
    )

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

    IcsExporter(alarm_minutes=config.ics.alarm_minutes).export(events, output)

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
