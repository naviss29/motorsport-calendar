"""Tests for GUI controller — no Flet dependency, mocked HTTP."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from motorsport_calendar.gui.controller import (
    generate_calendar,
    get_upcoming_weekend,
    list_championships,
)
from motorsport_calendar.models import (
    Championship,
    ChampionshipCategory,
    Circuit,
    Event,
    Session,
    SessionType,
)

# ---------------------------------------------------------------------------
# Minimal F2 fixture — 1 event, 4 sessions (2024 keys)
# ---------------------------------------------------------------------------

_F2_ONE_RACE = {
    "name": "Formula 2",
    "races": [
        {
            "name": "Bahrain Grand Prix",
            "location": "Sakhir",
            "round": 1,
            "slug": "bahrain",
            "localeKey": "bahrain",
            "sessions": {
                "fp1": "2024-02-29T11:05:00Z",
                "qualifying": "2024-03-01T12:10:00Z",
                "sprintRace": "2024-03-02T09:05:00Z",
                "feature": "2024-03-03T10:05:00Z",
            },
        }
    ],
}

_F2_EMPTY = {"name": "Formula 2", "races": []}


# ---------------------------------------------------------------------------
# TestListChampionships
# ---------------------------------------------------------------------------


class TestListChampionships:
    def test_returns_a_list(self) -> None:
        assert isinstance(list_championships(), list)

    def test_is_sorted(self) -> None:
        result = list_championships()
        assert result == sorted(result)

    def test_contains_formula1(self) -> None:
        assert "formula1" in list_championships()

    def test_contains_formula2(self) -> None:
        assert "formula2" in list_championships()

    def test_contains_formula3(self) -> None:
        assert "formula3" in list_championships()

    def test_contains_f1_academy(self) -> None:
        assert "f1-academy" in list_championships()

    def test_contains_wec(self) -> None:
        assert "wec" in list_championships()

    def test_idempotent(self) -> None:
        assert list_championships() == list_championships()


# ---------------------------------------------------------------------------
# TestGenerateCalendarEmptySelection
# ---------------------------------------------------------------------------


class TestGenerateCalendarEmptySelection:
    async def test_empty_ids_returns_empty_dict(self, tmp_path: Path) -> None:
        result = await generate_calendar(
            year=2025,
            championship_ids=[],
            output_path=str(tmp_path / "out.ics"),
        )
        assert result == {}

    async def test_no_ics_file_created_for_empty_selection(self, tmp_path: Path) -> None:
        output = tmp_path / "out.ics"
        await generate_calendar(year=2025, championship_ids=[], output_path=str(output))
        assert not output.exists()


# ---------------------------------------------------------------------------
# TestGenerateCalendarWec — NotImplementedError path
# ---------------------------------------------------------------------------


class TestGenerateCalendarWec:
    async def test_not_implemented_source_returns_error_string(self, tmp_path: Path) -> None:
        result = await generate_calendar(
            year=2025,
            championship_ids=["wec"],
            output_path=str(tmp_path / "out.ics"),
        )
        assert "wec" in result
        assert isinstance(result["wec"], str)

    async def test_error_string_contains_useful_text(self, tmp_path: Path) -> None:
        result = await generate_calendar(
            year=2025,
            championship_ids=["wec"],
            output_path=str(tmp_path / "out.ics"),
        )
        msg = result["wec"]
        assert isinstance(msg, str) and len(msg) > 0


# ---------------------------------------------------------------------------
# TestGenerateCalendarFormula2 — happy path
# ---------------------------------------------------------------------------


class TestGenerateCalendarFormula2:
    async def test_zero_events_returns_count_zero(self, tmp_path: Path) -> None:
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        with patch.object(F2Source, "fetch_json", AsyncMock(return_value=_F2_EMPTY)):
            result = await generate_calendar(
                year=2025,
                championship_ids=["formula2"],
                output_path=str(tmp_path / "out.ics"),
            )
        assert result.get("formula2") == (0, 0)

    async def test_zero_events_produces_no_file(self, tmp_path: Path) -> None:
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        output = tmp_path / "out.ics"
        with patch.object(F2Source, "fetch_json", AsyncMock(return_value=_F2_EMPTY)):
            await generate_calendar(
                year=2025,
                championship_ids=["formula2"],
                output_path=str(output),
            )
        assert not output.exists()

    async def test_one_event_returns_count_one(self, tmp_path: Path) -> None:
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        with patch.object(F2Source, "fetch_json", AsyncMock(return_value=_F2_ONE_RACE)):
            result = await generate_calendar(
                year=2024,
                championship_ids=["formula2"],
                output_path=str(tmp_path / "out.ics"),
            )
        # _F2_ONE_RACE has 1 event with 4 sessions (fp1, qualifying, sprintRace, feature)
        assert result.get("formula2") == (1, 4)

    async def test_one_event_creates_ics_file(self, tmp_path: Path) -> None:
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        output = tmp_path / "out.ics"
        with patch.object(F2Source, "fetch_json", AsyncMock(return_value=_F2_ONE_RACE)):
            await generate_calendar(
                year=2024,
                championship_ids=["formula2"],
                output_path=str(output),
            )
        assert output.exists()
        assert "BEGIN:VCALENDAR" in output.read_text(encoding="utf-8")

    async def test_ics_contains_correct_vevent_count(self, tmp_path: Path) -> None:
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        output = tmp_path / "out.ics"
        with patch.object(F2Source, "fetch_json", AsyncMock(return_value=_F2_ONE_RACE)):
            await generate_calendar(
                year=2024,
                championship_ids=["formula2"],
                output_path=str(output),
            )
        content = output.read_text(encoding="utf-8")
        # 1 event × 4 sessions = 4 VEVENTs
        assert content.count("BEGIN:VEVENT") == 4


# ---------------------------------------------------------------------------
# TestGenerateCalendarErrors
# ---------------------------------------------------------------------------


class TestGenerateCalendarErrors:
    async def test_http_404_returns_error_string(self, tmp_path: Path) -> None:
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(404, request=request)
        exc = httpx.HTTPStatusError("HTTP 404", request=request, response=response)

        with patch.object(F2Source, "fetch_json", AsyncMock(side_effect=exc)):
            result = await generate_calendar(
                year=2025,
                championship_ids=["formula2"],
                output_path=str(tmp_path / "out.ics"),
            )
        assert "404" in str(result.get("formula2"))

    async def test_timeout_returns_timeout_string(self, tmp_path: Path) -> None:
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        with patch.object(
            F2Source, "fetch_json", AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        ):
            result = await generate_calendar(
                year=2025,
                championship_ids=["formula2"],
                output_path=str(tmp_path / "out.ics"),
            )
        assert "timeout" in str(result.get("formula2")).lower()

    async def test_partial_failure_still_exports_successful(self, tmp_path: Path) -> None:
        """WEC fails (NotImplementedError) but F2 succeeds → ICS file still created."""
        from motorsport_calendar.providers.formula2.sources.f1calendar import (
            F1CalendarSource as F2Source,
        )

        output = tmp_path / "out.ics"
        with patch.object(F2Source, "fetch_json", AsyncMock(return_value=_F2_ONE_RACE)):
            result = await generate_calendar(
                year=2024,
                championship_ids=["formula2", "wec"],
                output_path=str(output),
            )
        assert isinstance(result.get("formula2"), tuple)
        assert isinstance(result.get("wec"), str)
        assert output.exists()


# ---------------------------------------------------------------------------
# TestGetUpcomingWeekend
# ---------------------------------------------------------------------------

# Non-WEC "Ce week-end" sources, one per championship — mocked at the
# get_season() level (Provider.fetch_events delegates straight to it), so
# no raw JSON fixtures are needed. WEC's OfficialWecSource always raises
# NotImplementedError for real — no mock required, matches production.
_WEEKEND_SOURCE_PATHS = {
    # ProvidersConfig defaults formula1 to the "openf1" source (see
    # config/models.py) — not the first-registered "jolpica" — mock that
    # one to match what get_upcoming_weekend actually calls.
    "formula1": "motorsport_calendar.providers.formula1.sources.openf1.OpenF1Source.get_season",
    "formula2": (
        "motorsport_calendar.providers.formula2.sources.f1calendar.F1CalendarSource.get_season"
    ),
    "formula3": (
        "motorsport_calendar.providers.formula3.sources.f1calendar.F1CalendarSource.get_season"
    ),
    "f1-academy": (
        "motorsport_calendar.providers.f1_academy.sources.f1calendar.F1CalendarSource.get_season"
    ),
}


@contextmanager
def patch_weekend_sources(events_by_championship: dict[str, list[Event]] | None = None):
    """Patch get_season() for the 4 non-WEC weekend championships.

    Each championship is fetched for 2 years (now.year and now.year + 1) —
    the mock only returns events whose season matches the requested year,
    so a fixture built for one year doesn't get double-counted on the
    second fetch call.
    """
    events_by_championship = events_by_championship or {}

    def _get_season_for(cid: str):
        async def _get_season(year: int) -> list[Event]:
            return [e for e in events_by_championship.get(cid, []) if e.season == year]

        return _get_season

    with ExitStack() as stack:
        for cid, target in _WEEKEND_SOURCE_PATHS.items():
            stack.enter_context(patch(target, side_effect=_get_season_for(cid)))
        yield


def _weekend_session(session_type: SessionType, start: datetime) -> Session:
    return Session(
        type=session_type,
        start_datetime=start,
        end_datetime=start + timedelta(hours=1),
        title=session_type.value,
    )


def _weekend_event(championship_id: str, *, start: datetime) -> Event:
    championship = Championship(
        id=championship_id, name=championship_id, category=ChampionshipCategory.SINGLE_SEATER
    )
    circuit = Circuit(
        id="test-circuit", name="Test Circuit", city="Test", country="France",
        timezone="Europe/Paris",
    )
    return Event(
        championship=championship,
        season=start.year,
        round=1,
        name="Test Grand Prix",
        circuit=circuit,
        sessions=(_weekend_session(SessionType.RACE, start),),
        event_uid=f"{championship_id}-1@test",
    )


# A Tuesday — the upcoming weekend is Friday 2026-07-10 to Sunday 2026-07-12.
_WEEKEND_NOW = datetime(2026, 7, 7, 12, 0, tzinfo=UTC)


class TestGetUpcomingWeekend:
    async def test_no_data_anywhere_returns_not_found(self) -> None:
        with patch_weekend_sources():
            result = await get_upcoming_weekend(now=_WEEKEND_NOW)
        assert result.found is False

    async def test_formula1_event_this_weekend_is_found(self) -> None:
        event = _weekend_event("formula1", start=datetime(2026, 7, 12, 13, 0, tzinfo=UTC))
        with patch_weekend_sources({"formula1": [event]}):
            result = await get_upcoming_weekend(now=_WEEKEND_NOW)
        assert result.found is True
        assert len(result.cards) == 1
        assert result.cards[0].championship_id == "formula1"

    async def test_wec_not_implemented_does_not_crash_the_whole_call(self) -> None:
        """WEC's real source always raises NotImplementedError — the other
        4 championships must still be attempted and the call must not raise.
        """
        with patch_weekend_sources():
            result = await get_upcoming_weekend(now=_WEEKEND_NOW)
        assert result.found is False  # nothing mocked in — but no crash

    async def test_partial_provider_failure_does_not_crash(self) -> None:
        event = _weekend_event("formula2", start=datetime(2026, 7, 11, 9, 0, tzinfo=UTC))
        with ExitStack() as stack:
            stack.enter_context(
                patch(
                    _WEEKEND_SOURCE_PATHS["formula1"],
                    AsyncMock(side_effect=httpx.TimeoutException("timeout")),
                )
            )
            stack.enter_context(
                patch(_WEEKEND_SOURCE_PATHS["formula2"], AsyncMock(return_value=[event]))
            )
            stack.enter_context(
                patch(_WEEKEND_SOURCE_PATHS["formula3"], AsyncMock(return_value=[]))
            )
            stack.enter_context(
                patch(_WEEKEND_SOURCE_PATHS["f1-academy"], AsyncMock(return_value=[]))
            )
            result = await get_upcoming_weekend(now=_WEEKEND_NOW)
        assert result.found is True
        assert result.cards[0].championship_id == "formula2"

    async def test_now_override_controls_which_weekend_is_searched(self) -> None:
        event = _weekend_event("formula1", start=datetime(2026, 8, 15, 13, 0, tzinfo=UTC))
        with patch_weekend_sources({"formula1": [event]}):
            result = await get_upcoming_weekend(now=_WEEKEND_NOW)
        assert result.found is True
        assert result.friday.isoformat() == "2026-08-14"
        assert result.sunday.isoformat() == "2026-08-16"

    async def test_default_now_is_used_when_omitted(self) -> None:
        """Calling without `now` must not raise — it defaults to the real
        current time internally. With every source mocked empty, there is
        nothing to find regardless of what "now" resolves to."""
        with patch_weekend_sources():
            result = await get_upcoming_weekend()
        assert result.found is False

    async def test_championship_with_no_registered_source_is_skipped(self) -> None:
        from motorsport_calendar.core.source_registry import source_registry

        with (
            patch_weekend_sources(),
            patch.object(source_registry, "list_for", return_value=[]),
        ):
            result = await get_upcoming_weekend(now=_WEEKEND_NOW)
        assert result.found is False

    async def test_championship_with_unregistered_provider_is_skipped(self) -> None:
        from motorsport_calendar.core.registry import registry

        with patch_weekend_sources(), patch.object(registry, "get", side_effect=KeyError("x")):
            result = await get_upcoming_weekend(now=_WEEKEND_NOW)
        assert result.found is False
