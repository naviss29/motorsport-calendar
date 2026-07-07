"""GUI controller — bridges the view to the existing engine.

No Flet import here: this module is testable in isolation.
Never duplicates providers, registry, exporter, or cache.
"""

from __future__ import annotations

from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from motorsport_calendar.gui.upcoming_weekend import WeekendResult


def list_championships() -> list[str]:
    """Return sorted list of all registered championship IDs."""
    from motorsport_calendar.core.registry import registry

    registry.discover()
    return registry.list_all()


async def get_upcoming_weekend(*, now: datetime | None = None) -> WeekendResult:
    """Find the next race weekend across the 5 "Ce week-end" championships.

    Mirrors ``generate_calendar``'s fetch pipeline exactly — same registries,
    same HttpCache, no new provider. ``refresh=False`` always: relies on the
    existing cache TTL so opening this page repeatedly does not hit the
    network every time. Never raises — a failing championship/year is
    skipped, matching the CLI's partial-failure resilience rule.

    Returns a ``upcoming_weekend.WeekendResult`` (found + display-ready
    cards, or not-found + a hint date for the next available weekend).
    """
    from motorsport_calendar.cache import HttpCache
    from motorsport_calendar.config import ConfigService
    from motorsport_calendar.config.models import ProviderConfig
    from motorsport_calendar.core.registry import registry
    from motorsport_calendar.core.source_registry import source_registry
    from motorsport_calendar.gui.upcoming_weekend import (
        WEEKEND_CHAMPIONSHIP_IDS,
        WeekendEntry,
        find_upcoming_weekend,
    )

    reference_now = now or datetime.now(UTC)

    config = ConfigService()
    cache: HttpCache | None = None
    if config.cache.enabled:
        cache = HttpCache(cache_dir=config.cache.resolved_path, ttl=config.cache.ttl_seconds)

    registry.discover()
    source_registry.discover()

    entries: list[WeekendEntry] = []

    for cid in WEEKEND_CHAMPIONSHIP_IDS:
        available = source_registry.list_for(cid)
        if not available:
            continue

        provider_cfg = config.providers.get(cid) or ProviderConfig()
        source_name = provider_cfg.source or available[0]

        try:
            make_source = source_registry.get(cid, source_name)
            make_provider = registry.get(cid)
        except KeyError:
            continue

        for year in (reference_now.year, reference_now.year + 1):
            source = make_source(cache, False)
            provider = make_provider(source)
            try:
                events = await provider.fetch_events(cid, year)
                entries.extend(WeekendEntry(championship_id=cid, event=e) for e in events)
            except Exception:  # one championship/year failing must not break the rest
                continue

    return find_upcoming_weekend(entries, now=reference_now)


async def generate_calendar(
    year: int,
    championship_ids: list[str],
    output_path: str,
    *,
    refresh: bool = False,
) -> dict[str, tuple[int, int] | str]:
    """Generate an ICS file for the selected championships.

    Mirrors the CLI ``generate`` pipeline without duplicating any logic.
    Returns a dict mapping each championship_id to either:
    - a tuple (event_count, session_count) on success
    - a str (error message) on failure

    Does NOT call asyncio.run() — intended to be awaited directly.
    """
    if not championship_ids:
        return {}

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

    provider_list: list[tuple[str, object]] = []
    results: dict[str, tuple[int, int] | str] = {}

    for cid in championship_ids:
        provider_cfg = config.providers.get(cid) or ProviderConfig()
        source_name = provider_cfg.source
        if not source_name:
            available = source_registry.list_for(cid)
            source_name = available[0] if available else ""

        if not source_name:
            results[cid] = "aucune source disponible"
            continue

        try:
            make_source = source_registry.get(cid, source_name)
            make_provider = registry.get(cid)
        except KeyError as exc:
            results[cid] = str(exc)
            continue

        source = make_source(cache, refresh)
        provider_list.append((cid, make_provider(source)))

    all_events: list = []

    for cid, provider in provider_list:
        try:
            events = await provider.fetch_events(cid, year)  # type: ignore[union-attr]
            all_events.extend(events)
            session_count = sum(len(e.sessions) for e in events)
            results[cid] = (len(events), session_count)
        except NotImplementedError:
            results[cid] = "source non implémentée"
        except httpx.HTTPStatusError as exc:
            results[cid] = f"HTTP {exc.response.status_code}"
        except httpx.TimeoutException:
            results[cid] = "timeout"
        except Exception as exc:  # noqa: BLE001
            results[cid] = str(exc)

    if all_events:
        all_events.sort(
            key=lambda e: min(
                (s.start_datetime for s in e.sessions),
                default=datetime.max.replace(tzinfo=timezone.utc),
            )
        )
        IcsExporter(alarm_minutes=config.ics.alarm_minutes).export(
            all_events, Path(output_path)
        )

    return results
