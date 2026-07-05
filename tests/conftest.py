"""Shared pytest fixtures."""

from datetime import datetime, timezone

import pytest

from motorsport_calendar.models import Championship, Circuit, Event, SessionType


@pytest.fixture
def sample_event() -> Event:
    return Event(
        id="f1-2025-01-race",
        name="Australian Grand Prix — Race",
        session_type=SessionType.RACE,
        start_time=datetime(2025, 3, 16, 5, 0, tzinfo=timezone.utc),
        end_time=datetime(2025, 3, 16, 7, 0, tzinfo=timezone.utc),
        timezone="Australia/Melbourne",
        round_number=1,
        championship_id="f1-2025",
        circuit_id="albert-park",
    )


@pytest.fixture
def sample_circuit() -> Circuit:
    return Circuit(
        id="albert-park",
        name="Albert Park Circuit",
        short_name="Albert Park",
        country="Australia",
        city="Melbourne",
        timezone="Australia/Melbourne",
        latitude=-37.8497,
        longitude=144.9680,
    )


@pytest.fixture
def sample_championship(sample_event: Event) -> Championship:
    return Championship(
        id="f1-2025",
        name="Formula 1 World Championship",
        short_name="F1",
        year=2025,
        sport="formula1",
        events=[sample_event],
    )
