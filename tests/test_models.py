"""Tests for Pydantic models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from motorsport_calendar.models import Championship, Circuit, Event, SessionType


class TestSessionType:
    def test_values_are_strings(self) -> None:
        assert SessionType.RACE == "race"
        assert SessionType.QUALIFYING == "qualifying"
        assert SessionType.PRACTICE_1 == "practice_1"

    def test_all_members_present(self) -> None:
        names = {s.value for s in SessionType}
        assert "race" in names
        assert "qualifying" in names
        assert "sprint" in names


class TestEvent:
    def test_creation(self, sample_event: Event) -> None:
        assert sample_event.id == "f1-2025-01-race"
        assert sample_event.session_type == SessionType.RACE
        assert sample_event.round_number == 1

    def test_optional_fields_default_to_none(self) -> None:
        event = Event(
            id="test",
            name="Test Session",
            session_type=SessionType.QUALIFYING,
            start_time=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            end_time=datetime(2025, 1, 1, 13, 0, tzinfo=timezone.utc),
            timezone="UTC",
        )
        assert event.round_number is None
        assert event.url is None
        assert event.notes is None

    def test_invalid_session_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            Event(
                id="test",
                name="Test",
                session_type="not_a_valid_type",  # type: ignore[arg-type]
                start_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
                timezone="UTC",
            )


class TestCircuit:
    def test_creation(self, sample_circuit: Circuit) -> None:
        assert sample_circuit.id == "albert-park"
        assert sample_circuit.country == "Australia"
        assert sample_circuit.timezone == "Australia/Melbourne"

    def test_latitude_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Circuit(
                id="invalid",
                name="Invalid",
                country="XX",
                timezone="UTC",
                latitude=91.0,  # out of bounds
            )

    def test_longitude_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Circuit(
                id="invalid",
                name="Invalid",
                country="XX",
                timezone="UTC",
                longitude=181.0,  # out of bounds
            )


class TestChampionship:
    def test_creation(self, sample_championship: Championship) -> None:
        assert sample_championship.id == "f1-2025"
        assert sample_championship.year == 2025
        assert len(sample_championship.events) == 1

    def test_empty_events_by_default(self) -> None:
        c = Championship(id="wec-2025", name="WEC", year=2025, sport="wec")
        assert c.events == []

    def test_year_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Championship(id="x", name="X", year=1900, sport="f1")
