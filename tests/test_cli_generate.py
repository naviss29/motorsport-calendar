"""Integration tests for the `motocal generate` CLI command.

Strategy:
- F1 : patch OpenF1Source._get_json avec AsyncMock (side_effect=[meetings, sessions])
- WEC : patch OfficialWecSource.get_season avec AsyncMock (return_value=wec_events)
- Pour les tests "tout échoue" : F1 mock → exception HTTP/timeout, WEC échoue naturellement
  (NotImplementedError, aucun mock nécessaire)
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from motorsport_calendar.cli import app
from motorsport_calendar.models import (
    Championship,
    ChampionshipCategory,
    Circuit,
    Event,
    Session,
    SessionType,
)
from motorsport_calendar.providers.formula1.sources.openf1 import OpenF1Source
from motorsport_calendar.providers.f1_academy.sources.f1calendar import F1CalendarSource as F1AcademyCalendarSource
from motorsport_calendar.providers.formula2.sources.f1calendar import F1CalendarSource as F2CalendarSource
from motorsport_calendar.providers.formula3.sources.f1calendar import F1CalendarSource as F3CalendarSource
from motorsport_calendar.providers.wec.sources.official import OfficialWecSource

runner = CliRunner()

# ---------------------------------------------------------------------------
# Données F1 — mirrors OpenF1 API response shape
# ---------------------------------------------------------------------------

_F1_MEETINGS = [
    {
        "meeting_key": 1217,
        "meeting_name": "Bahrain Grand Prix",
        "location": "Sakhir",
        "country_name": "Bahrain",
        "circuit_short_name": "Sakhir",
        "circuit_key": 1,
        "year": 2024,
        "date_start": "2024-02-29T09:00:00+00:00",
    },
    {
        "meeting_key": 1218,
        "meeting_name": "Saudi Arabian Grand Prix",
        "location": "Jeddah",
        "country_name": "Saudi Arabia",
        "circuit_short_name": "Jeddah",
        "circuit_key": 2,
        "year": 2024,
        "date_start": "2024-03-07T09:00:00+00:00",
    },
]

_F1_SESSIONS = [
    {
        "session_key": 9472,
        "meeting_key": 1217,
        "session_name": "Race",
        "date_start": "2024-03-02T15:00:00+00:00",
        "date_end": "2024-03-02T17:00:00+00:00",
    },
    {
        "session_key": 9473,
        "meeting_key": 1217,
        "session_name": "Qualifying",
        "date_start": "2024-03-01T15:00:00+00:00",
        "date_end": "2024-03-01T16:00:00+00:00",
    },
    {
        "session_key": 9490,
        "meeting_key": 1218,
        "session_name": "Race",
        "date_start": "2024-03-09T18:00:00+00:00",
        "date_end": "2024-03-09T20:00:00+00:00",
    },
]

_F1_SESSION_COUNT = 3  # 2 Bahrain + 1 Saudi

# ---------------------------------------------------------------------------
# Données WEC
# ---------------------------------------------------------------------------

_WEC_CHAMPIONSHIP = Championship(
    id="wec-2024",
    name="FIA World Endurance Championship",
    category=ChampionshipCategory.ENDURANCE,
)

_WEC_EVENTS = [
    Event(
        event_uid="wec-2024-01-sebring",
        championship=_WEC_CHAMPIONSHIP,
        season=2024,
        round=1,
        name="1000 Miles of Sebring",
        circuit=Circuit(
            id="sebring",
            name="Sebring International Raceway",
            city="Sebring",
            country="USA",
            timezone="America/New_York",
        ),
        sessions=(
            Session(
                type=SessionType.RACE,
                title="Race",
                start_datetime=datetime(2024, 3, 16, 16, 0, tzinfo=timezone.utc),
                end_datetime=datetime(2024, 3, 16, 22, 0, tzinfo=timezone.utc),
            ),
        ),
    ),
    Event(
        event_uid="wec-2024-02-spa",
        championship=_WEC_CHAMPIONSHIP,
        season=2024,
        round=2,
        name="6 Hours of Spa-Francorchamps",
        circuit=Circuit(
            id="spa",
            name="Circuit de Spa-Francorchamps",
            city="Spa",
            country="Belgium",
            timezone="Europe/Brussels",
        ),
        sessions=(
            Session(
                type=SessionType.HYPERPOLE,
                title="Hyperpole",
                start_datetime=datetime(2024, 5, 10, 9, 0, tzinfo=timezone.utc),
                end_datetime=datetime(2024, 5, 10, 9, 30, tzinfo=timezone.utc),
            ),
            Session(
                type=SessionType.RACE,
                title="Race",
                start_datetime=datetime(2024, 5, 11, 13, 0, tzinfo=timezone.utc),
                end_datetime=datetime(2024, 5, 11, 19, 0, tzinfo=timezone.utc),
            ),
        ),
    ),
]

_WEC_SESSION_COUNT = 3  # 1 Sebring + 2 Spa

# Événements WEC antérieurs à F1 — pour le test de tri chronologique
_WEC_EVENTS_EARLY = [
    Event(
        event_uid="wec-2024-01-daytona",
        championship=_WEC_CHAMPIONSHIP,
        season=2024,
        round=1,
        name="Rolex 24 at Daytona",
        circuit=Circuit(
            id="daytona",
            name="Daytona International Speedway",
            city="Daytona Beach",
            country="USA",
            timezone="America/New_York",
        ),
        sessions=(
            Session(
                type=SessionType.RACE,
                title="Race",
                # Janvier — avant tous les events F1 de mars
                start_datetime=datetime(2024, 1, 27, 14, 0, tzinfo=timezone.utc),
                end_datetime=datetime(2024, 1, 28, 14, 0, tzinfo=timezone.utc),
            ),
        ),
    )
]


def _mock_f1(meetings: list, sessions: list) -> AsyncMock:
    return AsyncMock(side_effect=[meetings, sessions])


def _mock_wec(events: list) -> AsyncMock:
    return AsyncMock(return_value=events)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestGenerateHappyPath:
    def test_f1_succeeds_wec_fails_exits_zero(self, tmp_path: Path) -> None:
        with patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert result.exit_code == 0

    def test_f1_succeeds_wec_fails_creates_file(self, tmp_path: Path) -> None:
        output = tmp_path / "all.ics"
        with patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)):
            runner.invoke(app, ["generate", "2024", str(output)])
        assert output.exists()
        assert output.stat().st_size > 0

    def test_f1_succeeds_wec_fails_vevent_count_is_f1_only(self, tmp_path: Path) -> None:
        output = tmp_path / "all.ics"
        with patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)):
            runner.invoke(app, ["generate", "2024", str(output)])
        content = output.read_text(encoding="utf-8")
        assert content.count("BEGIN:VEVENT") == _F1_SESSION_COUNT

    def test_both_succeed_exits_zero(self, tmp_path: Path) -> None:
        with (
            patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)),
            patch.object(OfficialWecSource, "get_season", _mock_wec(_WEC_EVENTS)),
        ):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert result.exit_code == 0

    def test_both_succeed_vevent_count_is_sum_of_all_sessions(self, tmp_path: Path) -> None:
        output = tmp_path / "all.ics"
        with (
            patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)),
            patch.object(OfficialWecSource, "get_season", _mock_wec(_WEC_EVENTS)),
        ):
            runner.invoke(app, ["generate", "2024", str(output)])
        content = output.read_text(encoding="utf-8")
        assert content.count("BEGIN:VEVENT") == _F1_SESSION_COUNT + _WEC_SESSION_COUNT

    def test_both_succeed_file_contains_vcalendar(self, tmp_path: Path) -> None:
        output = tmp_path / "all.ics"
        with (
            patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)),
            patch.object(OfficialWecSource, "get_season", _mock_wec(_WEC_EVENTS)),
        ):
            runner.invoke(app, ["generate", "2024", str(output)])
        content = output.read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in content
        assert "END:VCALENDAR" in content

    def test_f1_success_summary_shows_checkmark(self, tmp_path: Path) -> None:
        with patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert "✓" in result.output

    def test_wec_failure_summary_shows_failure_marker(self, tmp_path: Path) -> None:
        # WEC échoue naturellement (stub NotImplementedError)
        with patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert "✗" in result.output

    def test_empty_f1_season_still_exits_zero(self, tmp_path: Path) -> None:
        # 0 événements F1 mais fetch réussi → exit 0
        with patch.object(OpenF1Source, "_get_json", _mock_f1([], [])):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Error path
# ---------------------------------------------------------------------------


class TestGenerateErrors:
    def test_all_providers_fail_exits_one(self, tmp_path: Path) -> None:
        request = httpx.Request("GET", "https://api.openf1.org/v1/meetings")
        response = httpx.Response(503, request=request)
        http_fail = httpx.HTTPStatusError("503", request=request, response=response)
        f1_fail = AsyncMock(side_effect=http_fail)
        f2_fail = AsyncMock(side_effect=http_fail)
        f3_fail = AsyncMock(side_effect=http_fail)
        f1a_fail = AsyncMock(side_effect=http_fail)
        with (
            patch.object(OpenF1Source, "_get_json", f1_fail),
            patch.object(F2CalendarSource, "fetch_json", f2_fail),
            patch.object(F3CalendarSource, "fetch_json", f3_fail),
            patch.object(F1AcademyCalendarSource, "fetch_json", f1a_fail),
        ):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert result.exit_code == 1

    def test_all_providers_fail_no_file_created(self, tmp_path: Path) -> None:
        output = tmp_path / "all.ics"
        request = httpx.Request("GET", "https://api.openf1.org/v1/meetings")
        response = httpx.Response(503, request=request)
        http_fail = httpx.HTTPStatusError("503", request=request, response=response)
        f1_fail = AsyncMock(side_effect=http_fail)
        f2_fail = AsyncMock(side_effect=http_fail)
        f3_fail = AsyncMock(side_effect=http_fail)
        f1a_fail = AsyncMock(side_effect=http_fail)
        with (
            patch.object(OpenF1Source, "_get_json", f1_fail),
            patch.object(F2CalendarSource, "fetch_json", f2_fail),
            patch.object(F3CalendarSource, "fetch_json", f3_fail),
            patch.object(F1AcademyCalendarSource, "fetch_json", f1a_fail),
        ):
            runner.invoke(app, ["generate", "2024", str(output)])
        assert not output.exists()

    def test_f1_http_error_wec_succeeds_exits_zero(self, tmp_path: Path) -> None:
        request = httpx.Request("GET", "https://api.openf1.org/v1/meetings")
        response = httpx.Response(503, request=request)
        f1_fail = AsyncMock(
            side_effect=httpx.HTTPStatusError("503", request=request, response=response)
        )
        with (
            patch.object(OpenF1Source, "_get_json", f1_fail),
            patch.object(OfficialWecSource, "get_season", _mock_wec(_WEC_EVENTS)),
        ):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert result.exit_code == 0

    def test_f1_timeout_wec_succeeds_exits_zero(self, tmp_path: Path) -> None:
        request = httpx.Request("GET", "https://api.openf1.org/v1/meetings")
        f1_timeout = AsyncMock(side_effect=httpx.TimeoutException("timeout", request=request))
        with (
            patch.object(OpenF1Source, "_get_json", f1_timeout),
            patch.object(OfficialWecSource, "get_season", _mock_wec(_WEC_EVENTS)),
        ):
            result = runner.invoke(app, ["generate", "2024", str(tmp_path / "all.ics")])
        assert result.exit_code == 0

    def test_surviving_provider_events_exported_when_one_fails(self, tmp_path: Path) -> None:
        output = tmp_path / "all.ics"
        request = httpx.Request("GET", "https://api.openf1.org/v1/meetings")
        response = httpx.Response(503, request=request)
        f1_fail = AsyncMock(
            side_effect=httpx.HTTPStatusError("503", request=request, response=response)
        )
        with (
            patch.object(OpenF1Source, "_get_json", f1_fail),
            patch.object(OfficialWecSource, "get_season", _mock_wec(_WEC_EVENTS)),
        ):
            runner.invoke(app, ["generate", "2024", str(output)])
        content = output.read_text(encoding="utf-8")
        assert content.count("BEGIN:VEVENT") == _WEC_SESSION_COUNT


# ---------------------------------------------------------------------------
# --refresh flag
# ---------------------------------------------------------------------------


class TestGenerateRefresh:
    def test_refresh_flag_exits_zero(self, tmp_path: Path) -> None:
        with patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)):
            result = runner.invoke(
                app, ["generate", "2024", str(tmp_path / "all.ics"), "--refresh"]
            )
        assert result.exit_code == 0

    def test_refresh_flag_creates_file(self, tmp_path: Path) -> None:
        output = tmp_path / "all-refresh.ics"
        with patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)):
            runner.invoke(app, ["generate", "2024", str(output), "--refresh"])
        assert output.exists()


# ---------------------------------------------------------------------------
# Tri chronologique
# ---------------------------------------------------------------------------


class TestGenerateSorting:
    def test_events_sorted_chronologically(self, tmp_path: Path) -> None:
        """Les events WEC de janvier doivent apparaître avant les events F1 de mars."""
        output = tmp_path / "sorted.ics"
        with (
            patch.object(OpenF1Source, "_get_json", _mock_f1(_F1_MEETINGS, _F1_SESSIONS)),
            patch.object(OfficialWecSource, "get_season", _mock_wec(_WEC_EVENTS_EARLY)),
        ):
            runner.invoke(app, ["generate", "2024", str(output)])

        content = output.read_text(encoding="utf-8")
        vevents = content.split("BEGIN:VEVENT")
        # vevents[0] = header VCALENDAR, vevents[1] = premier VEVENT
        assert len(vevents) >= 2
        # Le premier VEVENT doit être Daytona (janvier 2024 → 20240127)
        assert "20240127" in vevents[1]
