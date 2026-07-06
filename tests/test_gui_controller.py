"""Tests for GUI controller — no Flet dependency, mocked HTTP."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from motorsport_calendar.gui.controller import generate_calendar, list_championships

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
        assert result.get("formula2") == 0

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
        assert result.get("formula2") == 1

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
        assert isinstance(result.get("formula2"), int)
        assert isinstance(result.get("wec"), str)
        assert output.exists()
