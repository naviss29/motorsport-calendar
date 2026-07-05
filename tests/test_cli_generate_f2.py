"""CLI integration tests for `motocal generate-f2`."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from motorsport_calendar.cli import app

runner = CliRunner()

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

_BAHRAIN_EVENT: dict[str, Any] = {
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

_MONACO_EVENT: dict[str, Any] = {
    "name": "Monaco Grand Prix",
    "location": "Monte-Carlo",
    "round": 8,
    "slug": "monaco",
    "localeKey": "monaco",
    "sessions": {
        "qualifying": "2024-05-24T13:00:00Z",
        "sprintRace": "2024-05-25T10:35:00Z",
        "feature": "2024-05-26T09:05:00Z",
    },
}

_F1CALENDAR_ONE_RACE: dict[str, Any] = {
    "name": "Formula 2",
    "events": [_BAHRAIN_EVENT],
}

_F1CALENDAR_TWO_RACES: dict[str, Any] = {
    "name": "Formula 2",
    "events": [_BAHRAIN_EVENT, _MONACO_EVENT],
}

_F1CALENDAR_EMPTY: dict[str, Any] = {
    "name": "Formula 2",
    "events": [],
}


def _run_generate_f2(
    year: int,
    output: Path,
    fetch_json_return: Any = _F1CALENDAR_ONE_RACE,
    extra_args: list[str] | None = None,
) -> Any:
    """Invoke `generate-f2` with a mocked F1CalendarSource.fetch_json."""
    args = ["generate-f2", str(year), str(output)] + (extra_args or [])
    with patch(
        "motorsport_calendar.providers.formula2.sources.f1calendar.F1CalendarSource.fetch_json",
        new=AsyncMock(return_value=fetch_json_return),
    ):
        return runner.invoke(app, args)


# ---------------------------------------------------------------------------
# TestGenerateF2HappyPath
# ---------------------------------------------------------------------------


class TestGenerateF2HappyPath:
    def test_exit_code_zero_on_success(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics")
        assert result.exit_code == 0, result.output

    def test_ics_file_created(self, tmp_path: Path) -> None:
        output = tmp_path / "f2.ics"
        _run_generate_f2(2024, output)
        assert output.exists()

    def test_ics_file_not_empty(self, tmp_path: Path) -> None:
        output = tmp_path / "f2.ics"
        _run_generate_f2(2024, output)
        assert output.stat().st_size > 0

    def test_ics_contains_vcalendar_header(self, tmp_path: Path) -> None:
        output = tmp_path / "f2.ics"
        _run_generate_f2(2024, output)
        assert "BEGIN:VCALENDAR" in output.read_text()

    def test_output_mentions_event_count(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics")
        assert "1 event" in result.output

    def test_output_mentions_year(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics")
        assert "2024" in result.output

    def test_output_mentions_source_name(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics")
        assert "f1calendar" in result.output

    def test_two_events_in_output(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics", _F1CALENDAR_TWO_RACES)
        assert "2 event" in result.output

    def test_empty_season_produces_empty_ics(self, tmp_path: Path) -> None:
        output = tmp_path / "f2.ics"
        result = _run_generate_f2(2024, output, _F1CALENDAR_EMPTY)
        assert result.exit_code == 0
        assert "0 event" in result.output

    def test_refresh_flag_accepted(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics", extra_args=["--refresh"])
        assert result.exit_code == 0

    def test_refresh_flag_noted_in_output(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics", extra_args=["--refresh"])
        assert "--refresh" in result.output

    def test_sessions_count_in_output(self, tmp_path: Path) -> None:
        result = _run_generate_f2(2024, tmp_path / "f2.ics")
        assert "session" in result.output


# ---------------------------------------------------------------------------
# TestGenerateF2Errors
# ---------------------------------------------------------------------------


class TestGenerateF2Errors:
    def test_http_error_exits_with_code_1(self, tmp_path: Path) -> None:
        import httpx

        request = httpx.Request("GET", "https://example.com")
        response = httpx.Response(404, request=request)
        exc = httpx.HTTPStatusError("HTTP 404", request=request, response=response)

        with patch(
            "motorsport_calendar.providers.formula2.sources.f1calendar.F1CalendarSource.fetch_json",
            new=AsyncMock(side_effect=exc),
        ):
            result = runner.invoke(app, ["generate-f2", "2024", str(tmp_path / "f2.ics")])

        assert result.exit_code == 1

    def test_timeout_exits_with_code_1(self, tmp_path: Path) -> None:
        import httpx

        with patch(
            "motorsport_calendar.providers.formula2.sources.f1calendar.F1CalendarSource.fetch_json",
            new=AsyncMock(side_effect=httpx.TimeoutException("timeout")),
        ):
            result = runner.invoke(app, ["generate-f2", "2024", str(tmp_path / "f2.ics")])

        assert result.exit_code == 1

    def test_missing_year_argument_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["generate-f2", str(tmp_path / "f2.ics")])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# TestGenerateF2IcsContent
# ---------------------------------------------------------------------------


class TestGenerateF2IcsContent:
    def test_ics_contains_vevent(self, tmp_path: Path) -> None:
        output = tmp_path / "f2.ics"
        _run_generate_f2(2024, output)
        assert "BEGIN:VEVENT" in output.read_text()

    def test_ics_contains_feature_race(self, tmp_path: Path) -> None:
        output = tmp_path / "f2.ics"
        _run_generate_f2(2024, output)
        content = output.read_text()
        assert "Feature Race" in content

    def test_ics_contains_qualifying(self, tmp_path: Path) -> None:
        output = tmp_path / "f2.ics"
        _run_generate_f2(2024, output)
        content = output.read_text()
        assert "Qualifying" in content
