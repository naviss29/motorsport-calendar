"""Shared pytest fixtures."""

from datetime import datetime, timezone

import pytest

from motorsport_calendar.models import (
    Championship,
    ChampionshipCategory,
    Circuit,
    Event,
    Session,
    SessionType,
)

TZ = timezone.utc


@pytest.fixture
def f1() -> Championship:
    return Championship(
        id="f1",
        name="Formula 1 World Championship",
        category=ChampionshipCategory.SINGLE_SEATER,
    )


@pytest.fixture
def albert_park() -> Circuit:
    return Circuit(
        id="albert-park",
        name="Albert Park Circuit",
        city="Melbourne",
        country="Australia",
        timezone="Australia/Melbourne",
    )


@pytest.fixture
def race_session() -> Session:
    return Session(
        type=SessionType.RACE,
        start_datetime=datetime(2025, 3, 16, 5, 0, tzinfo=TZ),
        end_datetime=datetime(2025, 3, 16, 7, 0, tzinfo=TZ),
        title="Australian Grand Prix — Race",
        description="Round 1 of the 2025 season.",
    )


@pytest.fixture
def qualifying_session() -> Session:
    return Session(
        type=SessionType.QUALIFYING,
        start_datetime=datetime(2025, 3, 15, 7, 0, tzinfo=TZ),
        end_datetime=datetime(2025, 3, 15, 8, 0, tzinfo=TZ),
        title="Australian Grand Prix — Qualifying",
    )


@pytest.fixture
def australian_gp(
    f1: Championship,
    albert_park: Circuit,
    race_session: Session,
    qualifying_session: Session,
) -> Event:
    return Event(
        championship=f1,
        season=2025,
        round=1,
        name="Australian Grand Prix",
        circuit=albert_park,
        sessions=(qualifying_session, race_session),
        event_uid="f1-2025-01-aus@motorsport-calendar",
    )
