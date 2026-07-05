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
    from motorsport_calendar.core.source_registry import source_registry
    from motorsport_calendar.exporters.ics import IcsExporter

    config = ConfigService()

    cache: HttpCache | None = None
    if config.cache.enabled:
        cache = HttpCache(
            cache_dir=config.cache.resolved_path,
            ttl=config.cache.ttl_seconds,
        )

    # Découverte automatique — la CLI ne connaît ni les providers ni les sources
    registry.discover()
    source_registry.discover()

    provider_cfg = config.providers.get("formula1")
    if provider_cfg is None:
        from motorsport_calendar.config.models import ProviderConfig
        provider_cfg = ProviderConfig(source="openf1")

    source_name = provider_cfg.source or "openf1"

    try:
        make_source = source_registry.get("formula1", source_name)
    except KeyError as exc:
        err_console.print(str(exc))
        raise typer.Exit(code=1)

    source = make_source(cache, refresh)

    try:
        make_provider = registry.get("formula1")
    except KeyError as exc:
        err_console.print(str(exc))
        raise typer.Exit(code=1)

    provider = make_provider(source)

    async def _fetch() -> list:
        return await provider.fetch_events("formula1", year)

    cache_note = " [yellow](--refresh)[/]" if refresh else ""
    console.print(
        f"Fetching F1 [bold cyan]{year}[/] calendar "
        f"via [green]{source_name}[/]…{cache_note}"
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


@app.command("generate-wec")
def generate_wec(
    year: Annotated[int, typer.Argument(help="WEC season year (e.g. 2024)")],
    output: Annotated[Path, typer.Argument(help="Destination .ics file")],
    refresh: Annotated[
        bool,
        typer.Option("--refresh", help="Ignorer le cache et re-télécharger les données."),
    ] = False,
) -> None:
    """Fetch the FIA WEC calendar and export it as an ICS file."""
    import asyncio

    import httpx

    from motorsport_calendar.cache import HttpCache
    from motorsport_calendar.config import ConfigService
    from motorsport_calendar.core.registry import registry
    from motorsport_calendar.core.source_registry import source_registry
    from motorsport_calendar.exporters.ics import IcsExporter

    config = ConfigService()

    cache: HttpCache | None = None
    if config.cache.enabled:
        cache = HttpCache(
            cache_dir=config.cache.resolved_path,
            ttl=config.cache.ttl_seconds,
        )

    registry.discover()
    source_registry.discover()

    provider_cfg = config.providers.get("wec")
    if provider_cfg is None:
        from motorsport_calendar.config.models import ProviderConfig
        provider_cfg = ProviderConfig(source="official")

    source_name = provider_cfg.source or "official"

    try:
        make_source = source_registry.get("wec", source_name)
    except KeyError as exc:
        err_console.print(str(exc))
        raise typer.Exit(code=1)

    source = make_source(cache, refresh)

    try:
        make_provider = registry.get("wec")
    except KeyError as exc:
        err_console.print(str(exc))
        raise typer.Exit(code=1)

    provider = make_provider(source)

    async def _fetch() -> list:
        return await provider.fetch_events("wec", year)

    cache_note = " [yellow](--refresh)[/]" if refresh else ""
    console.print(
        f"Fetching WEC [bold cyan]{year}[/] calendar "
        f"via [green]{source_name}[/]…{cache_note}"
    )

    try:
        events = asyncio.run(_fetch())
    except NotImplementedError:
        err_console.print(
            f"La source WEC '[bold]{source_name}[/]' n'est pas encore implémentée. "
            "Consulter le backlog pour l'état d'avancement."
        )
        raise typer.Exit(code=1)
    except httpx.HTTPStatusError as exc:
        err_console.print(
            f"WEC API error {exc.response.status_code}: {exc.request.url}"
        )
        raise typer.Exit(code=1)
    except httpx.TimeoutException:
        err_console.print("WEC API timeout (10 s). Try again later.")
        raise typer.Exit(code=1)

    IcsExporter(alarm_minutes=config.ics.alarm_minutes).export(events, output)

    count = len(events)
    sessions_count = sum(len(e.sessions) for e in events)
    console.print(
        f"[green]✓[/] {count} event{'s' if count != 1 else ''}, "
        f"{sessions_count} session{'s' if sessions_count != 1 else ''} → [bold]{output}[/]"
    )


@app.command("generate")
def generate(
    year: Annotated[int, typer.Argument(help="Season year (e.g. 2024)")],
    output: Annotated[Path, typer.Argument(help="Destination .ics file")],
    refresh: Annotated[
        bool,
        typer.Option("--refresh", help="Ignorer le cache et re-télécharger les données."),
    ] = False,
) -> None:
    """Fetch all enabled championships and export them as a single ICS file."""
    import asyncio
    from datetime import datetime, timezone as _tz
    from typing import Any

    import httpx

    from motorsport_calendar.cache import HttpCache
    from motorsport_calendar.config import ConfigService
    from motorsport_calendar.config.models import ProviderConfig
    from motorsport_calendar.core.registry import registry
    from motorsport_calendar.core.source_registry import source_registry
    from motorsport_calendar.exporters.ics import IcsExporter

    config = ConfigService()

    cache: HttpCache | None = None
    if config.cache.enabled:
        cache = HttpCache(
            cache_dir=config.cache.resolved_path,
            ttl=config.cache.ttl_seconds,
        )

    registry.discover()
    source_registry.discover()

    enabled_ids = registry.enabled(config.providers)

    if not enabled_ids:
        err_console.print("Aucun provider activé dans la configuration.")
        raise typer.Exit(code=1)

    n = len(enabled_ids)
    cache_note = " [yellow](--refresh)[/]" if refresh else ""
    console.print(
        f"Génération calendrier [bold cyan]{year}[/] — "
        f"{n} provider{'s' if n != 1 else ''} activé{'s' if n != 1 else ''}…{cache_note}"
    )

    provider_list: list[tuple[str, Any]] = []
    results: list[tuple[str, list, str | None]] = []

    for championship_id in enabled_ids:
        provider_cfg = config.providers.get(championship_id) or ProviderConfig()
        source_name = provider_cfg.source
        if not source_name:
            available = source_registry.list_for(championship_id)
            source_name = available[0] if available else ""

        if not source_name:
            results.append((championship_id, [], "aucune source disponible"))
            continue

        try:
            make_source = source_registry.get(championship_id, source_name)
            make_provider = registry.get(championship_id)
        except KeyError as exc:
            results.append((championship_id, [], str(exc)))
            continue

        source = make_source(cache, refresh)
        provider_list.append((championship_id, make_provider(source)))

    async def _fetch_all() -> list[tuple[str, list, str | None]]:
        fetch_results: list[tuple[str, list, str | None]] = []
        for cid, prov in provider_list:
            try:
                events = await prov.fetch_events(cid, year)
                fetch_results.append((cid, list(events), None))
            except NotImplementedError:
                fetch_results.append((cid, [], "source non implémentée"))
            except httpx.HTTPStatusError as exc:
                fetch_results.append((cid, [], f"HTTP {exc.response.status_code}"))
            except httpx.TimeoutException:
                fetch_results.append((cid, [], "timeout"))
            except Exception as exc:  # noqa: BLE001
                fetch_results.append((cid, [], str(exc)))
        return fetch_results

    results.extend(asyncio.run(_fetch_all()))

    all_events: list[Any] = []
    for cid, events, error in results:
        if error is None:
            count = len(events)
            console.print(
                f"  [green]✓[/] {cid} : {count} événement{'s' if count != 1 else ''}"
            )
            all_events.extend(events)
        else:
            console.print(f"  [red]✗[/] {cid} : {error}")

    if not any(error is None for _, _, error in results):
        err_console.print("\nAucun championnat n'a pu être exporté.")
        raise typer.Exit(code=1)

    all_events.sort(
        key=lambda e: min(
            (s.start_datetime for s in e.sessions),
            default=datetime.max.replace(tzinfo=_tz.utc),
        )
    )

    IcsExporter(alarm_minutes=config.ics.alarm_minutes).export(all_events, output)

    total_sessions = sum(len(e.sessions) for e in all_events)
    console.print(
        f"\nExport terminé : [bold]{output}[/] "
        f"({len(all_events)} événement{'s' if len(all_events) != 1 else ''}, "
        f"{total_sessions} session{'s' if total_sessions != 1 else ''})"
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
